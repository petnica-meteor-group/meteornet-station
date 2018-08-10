#!/usr/bin/env python3

import sys
import os
import shutil
import stat

original_dir = sys.argv[1]
temp_dir = sys.argv[2]
main_path = sys.argv[3]

for file in os.listdir(original_dir):
    path = os.path.join(original_dir, file)
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

for file in os.listdir(temp_dir):
    path = os.path.join(temp_dir, file)
    to_path = os.path.join(original_dir, file)
    if os.path.isfile(path):
        shutil.copyfile(path, to_path)
    elif os.path.isdir(path):
        shutil.copytree(path, to_path)
shutil.rmtree(temp_dir)

os.chmod(main_path, os.stat(main_path).st_mode | stat.S_IEXEC)
os.execv(sys.executable, [ sys.executable, main_path ])
