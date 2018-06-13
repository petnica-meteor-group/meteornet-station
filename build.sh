#!/bin/bash

cd "${0%/*}"
SCRIPT_DIR=$(pwd)

rm -rf build
mkdir -p build/$(basename $SCRIPT_DIR)
cd build/$(basename $SCRIPT_DIR)

function compile() {
    if [[ -x "$(command -v $CC)" && -x "$(command -v $CXX)" ]]; then
        echo "Compiling with: $CC and $CXX"
    else
        echo "Unsupported compilers: $CC and $CXX"
        return
    fi

    for c_file in $(find $SCRIPT_DIR/ucontroller -iname "*.c"); do
        $CC $OPTIONS -c $c_file -o $(basename $c_file).o
    done

    for cpp_file in $(find $SCRIPT_DIR/ucontroller -iname "*.cpp"); do
        $CXX $OPTIONS -c $cpp_file -o $(basename $cpp_file).o
    done

    $CC $OPTIONS *.o -o $OUTPUT

    success=$?

    rm -f *.o

    if [[ $success -eq 0 ]]; then
        echo "Done"
    else
        echo "Errors occured"
    fi
}

# Linux
CC=gcc
CXX=g++
OPTIONS="-shared -fPIC"
OUTPUT=ucontroller.so

compile

# Windows
CC=x86_64-w64-mingw32-gcc
CXX=x86_64-w64-mingw32-g++
OPTIONS="$OPTIONS -L$SCRIPT_DIR/ucontroller/serial-com/implementations -lws2_32"
OUTPUT=ucontroller.dll

compile

cp $SCRIPT_DIR/main.py .
