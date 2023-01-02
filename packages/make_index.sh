#!/usr/bin/bash

export PLATFORM=docker-debian
make build-all

NL=$'\n'

find . -name "*.pkg.tar.gz" | xargs cp -n -t ./archives
index=""
for file in ./archives/*.pkg.tar.gz; do
    base_name=$(basename $file)
    language=$(cut -d '-' -f 1 <<< $base_name)
    version=$(cut -d '-' -f 2 <<< $base_name | awk -F'.pkg.tar.gz' '{print $1}')
    sha=$(sha256sum $base_name | cut -d ' ' -f 1)
    url="https://github.com/ooliver1/dewel/raw/master/packages/archives/$base_name"
    index+="$NL$language,$version,$sha,$url"
done

echo $index > archives/index.csv
echo "run git lfs track packages/archives/*.pkg.tar.gz"
