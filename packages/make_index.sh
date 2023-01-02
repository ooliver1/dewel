#!/usr/bin/bash

export PLATFORM=docker-debian
make build-all

rm -f archives/index.csv
find . -name "*.pkg.tar.gz" -type f -not -path "./archives/*" | xargs cp --remove-destination -t ./archives

for file in ./archives/*.pkg.tar.gz; do
    base_name=$(basename $file)
    language=$(cut -d '-' -f 1 <<< $base_name)
    version=$(cut -d '-' -f 2 <<< $base_name | awk -F'.pkg.tar.gz' '{print $1}')
    sha=$(sha256sum $base_name | cut -d ' ' -f 1)
    url="https://github.com/ooliver1/dewel/releases/download/pkgs/$base_name"
    echo "$language,$version,$sha,$url" >> archives/index.csv
done

