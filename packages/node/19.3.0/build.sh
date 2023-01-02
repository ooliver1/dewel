#!/bin/bash
curl "https://nodejs.org/dist/v19.3.0/node-v19.3.0-linux-x64.tar.xz" -o node.tar.xz
tar -xvf node.tar.xz --strip-components=1
rm node.tar.xz
