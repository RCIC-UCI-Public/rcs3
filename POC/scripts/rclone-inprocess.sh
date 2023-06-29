#!/bin/bash

TZ=":US/Pacific" date

for F in $( find /tmp/*.log -mtime -14 ); do
        echo "==== $F ==== "
        tail -5000 $F | fgrep -e Transferred -e Checks | tail -3
        echo
done
