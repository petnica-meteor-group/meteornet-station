import requests
import datetime
import logging
import threading
import collections
import json
import os

QUEUE_FILENAME = 'queue.json'

class InfoUploader:

    def __init__(self, info_url, error_url, id, retry_delay=60):
        self.id = id
        self.info_url = info_url
        self.error_url = error_url
        self.queue_path = os.path.join(os.path.dirname(__file__), QUEUE_FILENAME)
        if os.path.exists(self.queue_path):
            self._load_queue()
        else:
            self.queue = collections.deque()
        self.queue_lock = threading.Lock()
        self.queue_condition = threading.Condition(self.queue_lock)
        self.ended = False
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.worker = threading.Thread(target=InfoUploader._loop, args=(self,))
        self.worker.start()

    def queue_info(self, info, timestamp):
        with self.queue_lock:
            self.queue.append((info, timestamp, False))
            self.queue_condition.notify()

    def queue_error(self, error, timestamp):
        with self.queue_lock:
            self.queue.append((error, timestamp, True))
            self.queue_condition.notify()

    def _store_queue(self):
        with open(self.queue_path, 'w') as outfile:
            json.dump(list(self.queue), outfile)

    def _load_queue(self):
        try:
            with open(self.queue_path, 'r') as infile:
                self.queue = collections.deque(json.load(infile))
        except json.JSONDecodeError:
            self.queue = collections.deque()
            os.remove(self.queue_path)

    def _loop(self):
        while True:
            with self.queue_lock:
                try:
                    if self.ended:
                        self._store_queue()
                        break
                    elif len(self.queue) > 0:
                        while len(self.queue) > 0:
                            data, timestamp, error = self.queue.popleft()
                            self._upload(data, timestamp, error)
                        self._store_queue()
                except requests.exceptions.ConnectionError:
                    self.logger.warning("Could not connect to server. Retrying in {} minutes.".format(str(self.retry_delay)))
                    self.queue.appendleft((data, timestamp, error))
                except requests.exceptions.RequestException as e:
                    self.logger.warning("Server connection returned an error ({}). Retrying in {} minutes.".format(
                        str(e),
                        str(self.retry_delay))
                    )
                    self.queue.appendleft((data, timestamp, error))
                self.queue_condition.wait(timeout=self.retry_delay)

    def _upload(self, data, timestamp, error=False):
        if error:
            data_all = { 'id' : self.id, 'error' : json.dumps(data), 'timestamp' : timestamp }
            url = self.error_url
            start_msg = "Sending an error to the server..."
            end_msg = "Error sent successfully."
        else:
            data_all = { 'id' : self.id, 'data' : json.dumps(data), 'timestamp' : timestamp }
            url = self.info_url
            start_msg = "Sending info to the server..."
            end_msg = "Info sent successfully."

        self.logger.info(start_msg)
        requests.post(url, data=data_all, verify=False).raise_for_status()
        self.logger.info(end_msg)

    def end(self):
        with self.queue_lock:
            self.ended = True
            self.queue_condition.notify()
        self.worker.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
