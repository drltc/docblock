#!/bin/sh

while true
do
    echo "starting nc"
    nc -l 11234 < socket.bin > /dev/null
done

