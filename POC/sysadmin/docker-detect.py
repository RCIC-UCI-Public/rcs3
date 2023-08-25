#!/bin/env python3

import os

def running_in_docker():
    # Check if the file indicating a Docker environment exists
    return os.path.exists('/.dockerenv')

if __name__ == "__main__":
    if running_in_docker():
        print("Running inside a Docker container.")
    else:
        print("Not running inside a Docker container.")
