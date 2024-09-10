# Use the latest version of Rocky Linux 8 as the base image
FROM rockylinux/rockylinux:8.9

# Note: all supported tags @ https://hub.docker.com/_/rockylinux

# Install desired packages via dnf
RUN dnf -y update
RUN dnf -y install \
    epel-release

# Python3.9 and selected packages
RUN dnf -y install alternatives python39 gcc python39-devel
RUN alternatives --set python3 /usr/bin/python3.9
RUN alternatives --set python /usr/bin/python3.9

# Upgrade pip and setuptools
RUN python3 -m ensurepip --upgrade

# Upgrade pip and setuptools explicitly
RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install pyyaml boto3 psutil distro

RUN dnf -y install \
    git \
    zip \
    vim \
    procps-ng \
    findutils \
    htop \
    parallel \
    jq \
    bc \
    man-db \
    cargo \
    cronie \
    curl \
    tcpdump \
    wget

# Get the latest version of rclone - v1.68.0 as of this writing - released 2024-09-09
RUN RCLONE_VERSION=$(curl -s https://downloads.rclone.org/version.txt | awk -F'[ \t]+' '{print $2}') && \
    if [ "$(arch)" == "aarch64" ]; then PKGARCH="arm64"; else PKGARCH="amd64"; fi && \
    curl -O "https://downloads.rclone.org/$RCLONE_VERSION/rclone-$RCLONE_VERSION-linux-$PKGARCH.rpm" && \
    dnf localinstall -y "rclone-$RCLONE_VERSION-linux-$PKGARCH.rpm" && \
    rm "rclone-$RCLONE_VERSION-linux-$PKGARCH.rpm"

## Download and install AWS CLI
RUN echo "Downloading AWS CLI package..." && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-$(arch).zip" -o "awscliv2.zip" && \
    echo "Unzipping package..." && \
    unzip awscliv2.zip && \
    echo "Installing AWS CLI..." && \
    ./aws/install && \
    echo "Clean up ..." && \
    rm -f awscliv2.zip && rm -rf aws


# python39-devel not needed
RUN dnf -y erase python39-devel && dnf -y clean all

# Set environment variable for RCS3_ROOT (persistent storage) and AWS_SHARED_CREDENTIALS_FILE
#
ENV RCS3_ROOT=/.rcs3
ENV AWS_SHARED_CREDENTIALS_FILE=/.rcs3/.aws/credentials
ENV PS1='RCS3 Docker @\h \w> '

# Entry point or command to run when the container starts
CMD /sbin/crond -np
