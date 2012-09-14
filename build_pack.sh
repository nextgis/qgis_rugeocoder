#!/bin/bash

#Build zip packet

#Create if need
rm -R /tmp/build_plugin/ru_geocoder
mkdir /tmp/build_plugin/
mkdir /tmp/build_plugin/ru_geocoder
cp -R ./src/* /tmp/build_plugin/ru_geocoder

#Clean
rm /tmp/build_plugin/ru_geocoder/*.pyc
rm /tmp/build_plugin/ru_geocoder.zip

cd /tmp/build_plugin/
zip -r ru_geocoder.zip ./ru_geocoder

echo "Pack for load: /tmp/build_plugin/ru_geocoder.zip"