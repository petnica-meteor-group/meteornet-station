import requests
import logging
import threading
import json
import os
import sqlite3

class JsonUploader:

    DB_FILENAME = 'json_uploader.db'

    def __init__(self, target_url, retry_delay=3600):
        self.target_url = target_url
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)

        db_path = os.path.join(os.path.dirname(__file__), JsonUploader.DB_FILENAME)
        if not os.path.exists(db_path):
            self.logger.debug("Database doesn't exist, creating...")
            self.db_connection = sqlite3.connect(db_path)
            self.db_connection.cursor().execute('CREATE TABLE queue (id INTEGER PRIMARY KEY, content TEXT, processed INTEGER)')
            self.db_connection.commit()
            self.logger.debug("Database successfully created.")
        else:
            self.db_connection = sqlite3.connect(db_path)

        self.work_lock = threading.Lock()
        self.work_condition = threading.Condition(self.work_lock)
        self.do_not_disturb = False
        self.ended = False
        self.worker = threading.Thread(target=JsonUploader._loop, args=(self,))
        self.worker.start()

    def queue(self, data):
        with self.work_lock:
            self.db_connection.cursor().execute('INSERT INTO queue VALUES (NULL, ?, ?)', (json.dumps(data), 0))
            self.db_connection.commit()
            if not self.do_not_disturb:
                self.work_condition.notify()

    def _loop(self):
        worker_db_connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), JsonUploader.DB_FILENAME))
        while True:
            with self.work_lock:
                current_status = None
                try:
                    if self.ended:
                        break
                    else:
                        first = True
                        for status in worker_db_connection.cursor().execute('SELECT * FROM queue'):
                            if first:
                                self.logger.info("Sending status to the server...")
                                first = False
                            if status[2] == 0:
                                worker_db_connection.cursor().execute('UPDATE queue SET processed = 1 WHERE id = ?', (status[0],))
                                worker_db_connection.commit()
                                current_status = status
                                requests.post(self.target_url, data=json.loads(status[1]), verify=False).raise_for_status()
                            worker_db_connection.cursor().execute('DELETE FROM queue WHERE id = ?', (status[0],))
                            worker_db_connection.commit()
                        if not first: self.logger.info("Status successfully sent.")
                    self.do_not_disturb = False
                    self.work_condition.wait()
                except requests.exceptions.ConnectionError:
                    self.logger.warning("Could not connect to server. Retrying in {} minutes.".format(str(self.retry_delay // 60)))
                    worker_db_connection.cursor().execute('UPDATE queue SET processed = 0 WHERE id = ?', (current_status[0],))
                    worker_db_connection.commit()
                    self.do_not_disturb = True
                    self.work_condition.wait(timeout=self.retry_delay)
                except requests.exceptions.RequestException as e:
                    self.logger.warning("Server connection returned an error ({}). Retrying in {} minutes.".format(
                        str(e), str(self.retry_delay // 60)))
                    worker_db_connection.cursor().execute('UPDATE queue SET processed = 0 WHERE id = ?', (current_status[0],))
                    worker_db_connection.commit()
                    self.do_not_disturb = True
                    self.work_condition.wait(timeout=self.retry_delay)
        worker_db_connection.close()

    def end(self):
        with self.work_lock:
            self.ended = True
            self.work_condition.notify()
        self.db_connection.close()
        self.worker.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
