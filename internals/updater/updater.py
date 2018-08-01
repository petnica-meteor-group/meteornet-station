import os
import sys
import shutil
import requests
import zipfile
import stat
from os import path

class Updater:

    def __init__(project_path, main_path, zip_url, preserve_files, version, version_url):
        self.project_path = project_name
        self.main_path = main_path
        self.zip_url = zip_url
        self.preserve_files = preserve_files
        self.version = version
        self.version_url = version_url

        self.project_path_old = self.project_path + "~"
        self.project_parent_path = path.dirname(self.project_path)
        self.project_name = path.basename(self.project_path)

        if path.exists(self.project_path_old):
            shutil.rmtree(self.project_path_old)

    def update_required():
        response = requests.get(self.version_url)
        if response.status_code == 200:
            return self.version < response.content
        return False

    def update():
        try:
            response = requests.get(self.zip_url, stream=True)

            zip_filename = self.project_name + ".zip"
            if response.status_code == 200:
                with open(zip_filename, 'wb') as zip:
                    zip.write(response.content)

                os.rename(self.project_path, self.project_path_old)

                zip = zipfile.ZipFile(zip_filename, 'r')
                zip.extractall(self.project_parent_path)
                zip.close()
                os.remove(zip_filename)

                for file in self.preserve_files:
                    shutil.copyfile(path.join(self.project_path_old, file), path.join(self.project_path, file))

                os.chmod(self.main_path, os.stat(self.main_path).st_mode | stat.S_IEXEC)
                os.execlp(self.main_path, self.main_path)
            else:
                return False
        except Exception:
            return False
