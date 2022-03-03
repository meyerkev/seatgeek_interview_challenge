#!/bin/bash
containers=$(docker ps | grep meyerkev | grep interview | cut -d " " -f 1)
if test -z ${containers?}; then
    exit 0
fi
docker kill ${containers}
