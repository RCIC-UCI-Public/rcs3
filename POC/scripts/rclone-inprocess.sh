#!/bin/bash

TZ=":US/Pacific" date

for F in $( find /tmp/*.log -mtime -7 ); do
        echo "==== $F ==== "
        tail -5000 $F | fgrep -e Transferred -A1 -B1 -e Checks -e Errors | tail -4
        echo
done
