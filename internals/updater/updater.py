import os
import sys
import shutil
import requests
import zipfile
import stat
from os.path import basename, dirname, join, exists
import logging

BOOTSTRAPPER_FILENAME = 'bootstapper.py'

class UpdateFailed(Exception):
    pass

class Updater:

    def __init__(self, project_path, main_path_inner, zip_url, preserve_files, version, version_url):
        self.project_path = project_path
        self.project_name = basename(self.project_path)
        self.project_path_temp = self.project_path + '~'
        self.main_path = join(self.project_path, main_path_inner)
        self.zip_url = zip_url
        self.preserve_files = preserve_files
        self.version = version
        self.version_url = version_url

        self.logger = logging.getLogger(self.__class__.__name__)

        if exists(join(dirname(self.project_path), BOOTSTRAPPER_FILENAME)):
            os.remove(join(dirname(self.project_path), BOOTSTRAPPER_FILENAME))
            self.logger.info("Switched to new version. Update successful.")

    def update_required(self):
        try:
            self.logger.info("Checking for updates...")
            response = requests.post(self.version_url, verify=False)
            response.raise_for_status()
            if self.version < response.text:
                self.logger.info("Update available.")
                return True
            else:
                self.logger.info("Station is up-to-date.")
                return False
        except requests.exceptions.ConnectionError:
            self.logger.warning("Could not connect to the update server.")
        except requests.exceptions.RequestException:
            self.logger.warning("The update server returned an error.")
        return False

    def update(self):
        try:
            self.logger.info("Starting update process. Downloading...")

            response = requests.post(self.zip_url, stream=True, verify=False)
            response.raise_for_status()

            zip_filename = self.project_name + ".zip"
            with open(zip_filename, 'wb') as zip:
                zip.write(response.content)

            self.logger.debug("Unzipping update.")
            zip = zipfile.ZipFile(zip_filename, 'r')
            extracted = zip.namelist()[0]
            zip.extractall(self.project_path)
            zip.close()
            os.remove(zip_filename)
            os.rename(join(self.project_path, extracted), self.project_path_temp)

            for file in self.preserve_files:
                if exists(join(self.project_path, file)):
                    shutil.copyfile(join(self.project_path, file), join(self.project_path_temp, file))

            bootstrapper_path = join(dirname(self.project_path), BOOTSTRAPPER_FILENAME)
            shutil.copyfile(join(dirname(__file__), BOOTSTRAPPER_FILENAME), bootstrapper_path)

            self.logger.info("Update downloaded, switching to new version...")
            os.execv(sys.executable, [ sys.executable, bootstrapper_path,
                                       self.project_path, self.project_path_temp, self.main_path])
        except requests.exceptions.ConnectionError:
            warning = "Could not connect to the update server."
            self.logger.warning(warning)
            raise UpdateFailed(warning)
        except requests.exceptions.RequestException:
            warning = "The update server returned an error."
            self.logger.warning(warning)
            raise UpdateFailed(warning)

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
