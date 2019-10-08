#!/bin/sh

for id in `ps -aef | grep 'test' | awk  '/[0-9]+/{ print $2 }'`
do
    echo "kill:" $id
    sudo kill -9 $id
done
#docker container ls -a

