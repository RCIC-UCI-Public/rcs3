#!/usr/bin/env python3

import platform
import psutil
import math
import os
import distro

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
        distribution = (distro.name(),distro.version(),distro.codename())

    # Check if running inside a Docker container
    inside_docker = "Yes" if os.path.exists("/.dockerenv") else "No"

    return operating_system, arch, total_memory_gb, num_cores, hyperthreading_enabled, distribution, inside_docker

if __name__ == "__main__":
    operating_system, arch, total_memory_gb, num_cores, hyperthreading_enabled, distribution, inside_docker = detect_system_info()
    print("Operating System:", operating_system)
    print("Distribution:", distribution)
    print("Operating System Architecture:", arch)
    print("Total Memory (GB):", total_memory_gb)
    print("Number of CPU Cores:", num_cores)
    print("Hyperthreading Enabled:", hyperthreading_enabled)
    print("Running Inside Docker:", inside_docker)

