#!/usr/bin/env python3
# Class to generate the Commands

import argparse
import os
import subprocess
import platform
import sys
import stat
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(scriptdir)

BACKUP_SCRIPT_PATH = os.path.join(scriptdir,"gen-backup.py")
WINDOWS="WINDOWS"
UNIX="UNIX"
TEMPLATE= "{pythonpath} {script} --threads={threads} --checkers={checkers} --owner={owner} --system={system} {extra} run"

class ScriptGen:
    """Generate the sync/topup backup scripts for both Windows and Unix"""

    def __init__(self,owner,system,checkers=32,threads=2,logfile=None,OS_platform=None):
         self._owner = owner
         self._threads = threads
         self._checkers = checkers
         self.set_platform(OS_platform)
         if system is None:
            self._system = self.get_system_name()
         else:
            self._system = system
         ## Additional vars needed for Windows
         self._RCS3ROOT=os.path.join(scriptdir,"..","..")
         self._LOCALBIN=os.path.join(self._RCS3ROOT,"..","bin")
         self._LOCKFILE=os.path.join(self._RCS3ROOT,"..","gen-backup.lock")
         self._PYTHON=os.path.join(self._RCS3ROOT,"..","python311","python.exe")
         self._RCLONE=os.path.join(self._LOCALBIN,"rclone.exe")
         ## Set Script Headers
         if self._platform is UNIX:
               self._logfile = "/var/log/gen-backup.log" if logfile is None else logfile
               self._header="#!/bin/bash\n"
         else:
               self._logfile = os.path.join(self._RCS3ROOT,"..","gen-backup.log") if logfile is None else logfile
               self._header="#Powershell Script\n"
         self._header += "".join(["# ---     RCS3 BACKUP    ---\n","#     (C) 2024 UC-Regents\n"])

         ## Generate the daily and weekly sync commands
         self.set_sync_commands()
         
    def set_platform(self,OS_platform):
        """Derive the platform is not set"""
        if OS_platform is not None:
           self._platform = OS_platform
           return
        if platform.system() == "Windows":
           self._platform = WINDOWS
        else:
           self._platform = UNIX

    def get_system_name(self):
        """guess the name of the system"""  
        if self_platform is WINDOWS :
            return platform.uname().node
        else:
            return os.uname()[1]

    def set_sync_commands(self):
        template = TEMPLATE
        pextra = ""
        pythonpath = ""
        if self._platform == WINDOWS: 
            pythonpath=self._PYTHON
            winextra = f" --rclonecmd={self._RCLONE} --lockfile={self._LOCKFILE} $($args[0..$($args.length - 1)])"
            pextra += winextra
        else:
            pextra += " $@"

        self._weekly=template.format(pythonpath=pythonpath,script=BACKUP_SCRIPT_PATH, \
                      owner=self._owner,system=self._system, \
                      threads=self._threads,checkers=self._checkers,extra=pextra) 

        self._daily=template.format(pythonpath=pythonpath,script=BACKUP_SCRIPT_PATH, \
                      owner=self._owner,system=self._system, \
                      threads=self._threads,checkers=self._checkers,extra=pextra + " --top-up=24h") 


    def write_syncScript(self,filename=None,force=False):
        defFileName="weekly-backup" if self._platform is UNIX else "weekly-backup.ps1"
        self.write_script(self._weekly,defFileName,filename,force)

    def write_topupScript(self,filename=None,force=False):
        defFileName="daily-backup" if self._platform is UNIX else "daily-backup.ps1"
        self.write_script(self._daily,defFileName,filename,force)

    def write_script(self,basecmd,defFileName,filename,force):
        commandline=f"{basecmd} >> {self._logfile} 2>&1\n"
        scontents="".join([self._header,commandline])
        if filename is None:
           filename = os.path.join(scriptdir,"..","config",defFileName)
        self.writefile(scontents,filename,force)

    def writefile(self,contents,filename,force):
        if filename is sys.stdout:
           sys.stdout.write(contents)
        else:
           if not os.path.exists(filename) or (os.path.exists(filename) and force):
              with open(filename,"w") as f:
                 f.write(contents)
                 f.close()
                 st = os.stat(filename)
                 os.chmod(filename, st.st_mode | stat.S_IEXEC)
               
    def __str__(self):
        return (self._weekly + "\n" + self._daily)

def main():
    """ Command line to write the sync scripts """
    parser = argparse.ArgumentParser(description='Create a backup script')
    parser.add_argument('--daily', action='store_true', help='Generate a daily backup script')
    parser.add_argument('--weekly', action='store_true', help='Generate a weekly backup script')
    parser.add_argument('--threads', type=int, required=False, default=2, help='Number of threads (2)')
    parser.add_argument('--checkers', type=int, required=False,default=32, help='Number of checkers (32)')
    parser.add_argument('--owner', type=str, required=True, help='Owner name')
    parser.add_argument('--system', type=str, required=False, default=None, help='Name of System')
    parser.add_argument('--log', type=str, default=None, help='Log file path')
    parser.add_argument('--force', default=False,action='store_true', help='Force write file')

    args = parser.parse_args()

    if args.daily and args.weekly:
        print("Please choose either --daily or --weekly, not both.")
        return
    elif not args.daily and not args.weekly:
        print("Please choose either --daily or --weekly.")
        return

    syncScripts=ScriptGen(args.owner,args.system,checkers=args.checkers,threads=args.threads,logfile=args.log)
    backup_type = 'daily' if args.daily else 'weekly'
    if backup_type == 'daily':
         syncScripts.write_topupScript(force=args.force)
    else:
         syncScripts.write_syncScript(force=args.force)

if __name__ == '__main__':
    main()
