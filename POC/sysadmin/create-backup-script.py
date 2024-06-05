#!/usr/bin/env python3

import argparse
import os
import subprocess
import platform

scriptdir=os.path.realpath(os.path.dirname(__file__))

#sys.path.append(scriptdir)

BACKUP_SCRIPT_PATH = os.path.join(scriptdir,"gen-backup.py")

def get_system_name():
 
    if platform.system() == "Windows":
        return platform.uname().node
    else:
        return os.uname()[1]

def generate_cron_script(backup_type, threads, checkers, owner, system, log):
    if backup_type == 'weekly':
        cron_script = f"({BACKUP_SCRIPT_PATH} --threads={threads} --checkers={checkers} --owner={owner} --system={system} run > {log} 2>&1) &"
    elif backup_type == 'daily':
        cron_script = f"({BACKUP_SCRIPT_PATH} --owner={owner} --system={system} --top-up=24h run >> {log} 2>&1) &"
    else:
        raise ValueError("Invalid backup type. Choose 'daily' or 'weekly'.")

    return cron_script

def main():
    parser = argparse.ArgumentParser(description='Create a backup script')
    parser.add_argument('--daily', action='store_true', help='Generate a daily backup script')
    parser.add_argument('--weekly', action='store_true', help='Generate a weekly backup script')
    parser.add_argument('--threads', type=int, required=False, default=2, help='Number of threads (2)')
    parser.add_argument('--checkers', type=int, required=False,default=32, help='Number of checkers (32)')
    parser.add_argument('--owner', type=str, required=True, help='Owner name')
    parser.add_argument('--system', type=str, required=False, default=None, help='Name of System (%s)' % get_system_name())
    parser.add_argument('--log', type=str, default='/var/log/gen-backup.log', help='Log file path')

    args = parser.parse_args()

    if args.daily and args.weekly:
        print("Please choose either --daily or --weekly, not both.")
        return
    elif not args.daily and not args.weekly:
        print("Please choose either --daily or --weekly.")
        return

    system_name = args.system
    if system_name is None:
        system_name = get_system_name()
    backup_type = 'daily' if args.daily else 'weekly'
    cron_script = generate_cron_script(backup_type, args.threads, args.checkers, args.owner, system_name, args.log)

    if backup_type == 'daily':
        output_file = os.path.join(scriptdir,"..","config","daily-backup")
    else:
        output_file = os.path.join(scriptdir,"..","config","weekly-backup")
       
    with open(output_file, 'w') as file:
        file.write(cron_script + '\n')

    print(f"Cron script written to {output_file}")

if __name__ == '__main__':
    main()
