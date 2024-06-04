#!/usr/bin/env python3

import argparse
import os
import subprocess

BACKUP_SCRIPT_PATH = "/.rcs3/rcs3/POC/sysadmin/gen-backup.py"

def get_system_name():
    try:
        result = subprocess.run(['uname', '-n'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Unable to determine system name using 'uname -n'")

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
    parser.add_argument('--threads', type=int, required=True, help='Number of threads')
    parser.add_argument('--checkers', type=int, required=True, help='Number of checkers')
    parser.add_argument('--owner', type=str, required=True, help='Owner name')
    parser.add_argument('--log', type=str, default='/var/log/gen-backup.log', help='Log file path')

    args = parser.parse_args()

    if args.daily and args.weekly:
        print("Please choose either --daily or --weekly, not both.")
        return
    elif not args.daily and not args.weekly:
        print("Please choose either --daily or --weekly.")
        return

    system_name = get_system_name()
    backup_type = 'daily' if args.daily else 'weekly'
    cron_script = generate_cron_script(backup_type, args.threads, args.checkers, args.owner, system_name, args.log)

    output_file = '../config/daily-backup' if backup_type == 'daily' else '../config/weekly-backup'

    with open(output_file, 'w') as file:
        file.write(cron_script + '\n')

    print(f"Cron script written to {output_file}")

if __name__ == '__main__':
    main()
