#!/bin/bash

# Check if the dpkg command exists
if command -v dpkg &>/dev/null; then
  # If it exists, then the system is dpkg-based
  echo "This system is dpkg-based."
elif command -v rpm &>/dev/null; then
  # If it exists, then the system is RPM-based
  echo "This system is RPM-based."
else
  # If neither command exists, then the system uses a different packaging format
  echo "This system is not RPM-based or dpkg-based."
fi
