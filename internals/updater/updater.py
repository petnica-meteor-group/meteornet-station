import os
import sys
import shutil
import requests
import zipfile
import stat
from os.path import basename, dirname, join, exists
import logging
import importlib

BOOTSTRAPPER_FILENAME = 'bootstrapper.py'

class UpdateFailed(Exception):
    pass

class Updater:

    def __init__(self, config):
        self.project_path = config.PROJECT_PATH
        self.project_name = basename(self.project_path)
        self.project_path_temp = self.project_path + '~'
        self.main_path = join(self.project_path, config.MAIN_RELPATH)
        self.zip_url = config.URL_CODE_DOWNLOAD
        self.preserve_files = config.PRESERVE_FILES
        self.config_relpath = config.CONFIG_RELPATH
        self.version = config.VERSION
        self.version_url = config.URL_VERSION

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

            spec = importlib.util.spec_from_file_location(
                "internals.config",
                join(self.project_path_temp, self.config_relpath)
            )
            new_config = spec.loader.exec_module(importlib.util.module_from_spec(spec))
            for i, filepath in enumerate(self.preserve_files):
                new_filepath = new_config.PRESERVE_FILES[i]
                if exists(join(self.project_path, filepath)) and new_filepath:
                    shutil.copyfile(join(self.project_path, filepath), join(self.project_path_temp, new_filepath))

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
        except Exception as e:
            def get_trace(exception):
                import traceback
                return str(''.join(traceback.format_tb(exception.__traceback__))) + str(exception)

            warning = "Unhandled exception during update: " + str(get_trace(e))
            self.logger.warning(warning)
            if exists(self.project_path_temp):
                shutil.rmtree(self.project_path_temp)
            raise UpdateFailed(warning)

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
