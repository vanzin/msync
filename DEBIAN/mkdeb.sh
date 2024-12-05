#!/bin/bash

cd "$(dirname $0)"/../

ROOT=$(pwd)
BUILD=build/msync

rm -rf build
mkdir -p $BUILD
cp -r DEBIAN $BUILD
cd $BUILD

mkdir -p usr/share/applications
cp $ROOT/org.vanzin.msync.desktop usr/share/applications

mkdir -p usr/share/msync
cp -r $ROOT/src/* usr/share/msync
rm -rf usr/share/msync/__pycache__

mkdir -p usr/bin
(cd usr/bin && ln -sf ../share/msync/msync)

cd ..
dpkg-deb --build msync
