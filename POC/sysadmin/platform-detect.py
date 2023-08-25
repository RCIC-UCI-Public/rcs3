#!/bin/env python3

import platform
import psutil
import math

def detect_system_info():
    # Detect operating system
    operating_system = platform.system()

    # Detect operating system architecture
    arch = platform.architecture()[0]

    # Detect total memory in bytes
    total_memory = psutil.virtual_memory().total

    # Detect the number of CPU cores and hyperthreading status
    num_cores = psutil.cpu_count(logical=False)
    hyperthreading_enabled = psutil.cpu_count(logical=True) > num_cores

    # Convert memory to GB and round down
    total_memory_gb = math.floor(total_memory / (1024 ** 3))

    # Additional details for Linux distributions
    distribution = ""
    if operating_system == "Linux":
        distribution = platform.linux_distribution()

    return operating_system, arch, total_memory_gb, num_cores, hyperthreading_enabled, distribution

if __name__ == "__main__":
    operating_system, arch, total_memory_gb, num_cores, hyperthreading_enabled, distribution = detect_system_info()
    print("Operating System:", operating_system)
    print("Operating System Architecture:", arch)
    print("Total Memory (GB):", total_memory_gb)
    print("Number of CPU Cores:", num_cores)
    print("Hyperthreading Enabled:", hyperthreading_enabled)
    print("Distribution:", distribution)

