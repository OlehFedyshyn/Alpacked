#!/bin/bash

mkdir -p layer/nodejs

cd layer/nodejs

cp ../../package.json package.json

npm install

rm -rf package*.json