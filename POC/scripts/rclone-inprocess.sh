#!/bin/bash

TZ=":US/Pacific" date

for F in $( echo /tmp/backup-*.log); do
	echo "==== $F ==== "
	tail -5000 $F | fgrep -w Transferred | tail -2
	echo
done
