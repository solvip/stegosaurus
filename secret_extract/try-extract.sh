#!/bin/bash

I=0

while true; do
	./extract-file.sh
	if [ $? -ne 0 ]; then
		exit 0;
		echo $I
	fi
	I=$((I + 1))
	echo "At level: $I"
done
