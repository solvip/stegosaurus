#!/bin/bash

TYPE=$(file --mime-type secret | awk -F: '{print $2}' | tr -d ' ')

if [ "$TYPE" == "application/x-gzip" ]; then
	mv secret secret.gz
	gunzip secret.gz

	exit 0
fi

if [ "$TYPE" == "application/zip" ]; then
	mv secret secret.zip
	unzip secret.zip

	exit 0
fi

if [ "$TYPE" == "application/x-rar" ]; then
	mv secret secret.rar
	unrar e secret.rar

	exit 0
fi

echo "I do not recognize $TYPE"
exit 1
