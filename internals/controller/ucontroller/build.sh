#!/bin/bash

cd "${0%/*}"

function compile() {
    if [[ -x "$(command -v $CC)" && -x "$(command -v $CXX)" ]]; then
        echo "Compiling with: $CC and $CXX"
    else
        echo "Unsupported compilers: $CC and/or $CXX"
        return
    fi

    for c_file in $(find . -iname "*.c"); do
        $CC $OPTIONS -c $c_file -o $(basename $c_file).o
    done

    for cpp_file in $(find . -iname "*.cpp"); do
        $CXX $OPTIONS -c $cpp_file -o $(basename $cpp_file).o
    done

    $CC $OPTIONS *.o -o $OUTPUT

    success=$?

    rm -f *.o

    if [[ $success -eq 0 ]]; then
        echo "Done."
    else
        echo "Errors occurred."
    fi
}

STANDARD_OPTIONS="-shared -fPIC"

# Linux 32-bit
CC=gcc
CXX=g++
OPTIONS="$STANDARD_OPTIONS -m32"
OUTPUT=ucontroller32.so

compile

# Linux 64-bit
CC=gcc
CXX=g++
OPTIONS="$STANDARD_OPTIONS"
OUTPUT=ucontroller64.so

compile

# Windows 32-bit
CC=i686-w64-mingw32-gcc
CXX=i686-w64-mingw32-g++
OPTIONS="$STANDARD_OPTIONS"
OUTPUT=ucontroller32.dll

compile

# Windows 64-bit
CC=x86_64-w64-mingw32-gcc
CXX=x86_64-w64-mingw32-g++
OPTIONS="$STANDARD_OPTIONS"
OUTPUT=ucontroller64.dll

compile

# Build for Linux
#mkdir -p $BUILD_DIR/temp
#pyinstaller --clean --win-private-assemblies --distpath $BUILD_DIR --workpath $BUILD_DIR/temp --onefile -n $PROJECT_NAME main.py
#rm -rf $BUILD_DIR/temp

# Build for Windows
#mkdir -p $BUILD_DIR/temp
#wineconsole pyinstaller --clean --win-private-assemblies --distpath $BUILD_DIR --workpath $BUILD_DIR/temp --onefile -n $PROJECT_NAME main.py
#rm -rf $BUILD_DIR/temp

#rm $PROJECT_NAME.spec
