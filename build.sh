#!/bin/bash

cd "${0%/*}"
SCRIPT_DIR=$(pwd)

rm -rf build
mkdir -p build/$(basename $SCRIPT_DIR)
cd build/$(basename $SCRIPT_DIR)

while [[ "$#" > 0 ]]; do case $1 in
  -l|--linux) linux=1; shift;;
  -w|--windows) windows=1;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

if [[ ! $windows && ! $linux ]]; then
    echo "Please specify platform: --linux or --windows"
    exit 1
fi

CC=gcc
CXX=g++
OUTPUT=ucontroller.so
OPTIONS="-shared -fPIC"

if [[ $windows ]]; then
    CC=mingw32-gcc
    CXX=mingw32-g++
    OUTPUT=ucontroller.dll
fi

for c_file in $(find $SCRIPT_DIR/ucontroller -iname "*.c"); do
    $CC $OPTIONS -c $c_file -o $(basename $c_file).o
done

for cpp_file in $(find $SCRIPT_DIR/ucontroller -iname "*.cpp"); do
    $CXX $OPTIONS -c $cpp_file -o $(basename $cpp_file).o
done

$CC $OPTIONS *.o -o $OUTPUT

rm -f *.o
cp $SCRIPT_DIR/main.py .
