#!/bin/bash

find / -mindepth 1 -maxdepth 1 -type d -not \( -path 'bin' -o -name 'boot' -o -name 'etc*' -o -name 'etc' -o -name 'initrd' -o -name 'mnt' -o -name 'root' -o -name 'tmp*' -o -name 'opt' -o -name 'lost+found' -o -name sys -o -name run -o -name var -o -name proc -o -name '.log.*' -o -name 'config' -o -name 'var*' -o -name '.old*' -o -name .syno -o -name .system_info -o -name dev -o -name usr -o -name home -o -name media -o -name srv \) -print | sort
