# Use the latest version of Rocky Linux 8 as the base image
FROM rockylinux/rockylinux:8

# Install desired packages via yum
RUN yum -y update
RUN yum -y install \
    epel-release 

# Python3.9 and selected packages
RUN yum -y install alternatives python39
RUN alternatives --set python3 /usr/bin/python3.9
RUN alternatives --set python /usr/bin/python3.9
RUN python3 -m pip install pyyaml boto3 psutil distro 

RUN yum -y install \
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
    wget

# Get the latest version of rclone - v1.65.2 as of this writing
RUN RCLONE_VERSION=$(curl -s https://downloads.rclone.org/version.txt | awk -F'[ \t]+' '{print $2}') && \
    curl -O "https://downloads.rclone.org/$RCLONE_VERSION/rclone-$RCLONE_VERSION-linux-amd64.rpm" && \
    yum localinstall -y "rclone-$RCLONE_VERSION-linux-amd64.rpm" && \
    rm "rclone-$RCLONE_VERSION-linux-amd64.rpm"

# Download and install AWS CLI
RUN echo "Downloading AWS CLI package..." && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    echo "Unzipping package..." && \
    unzip awscliv2.zip && \
    echo "Installing AWS CLI..." && \
    ./aws/install && \
    echo "Clean up ..." && \
    rm -f awscliv2.zip && \
    rm -rf aws

# Set environment variable for RCS3_ROOT (persistent storage) and AWS_SHARED_CREDENTIALS_FILE
# 
ENV RCS3_ROOT=/.rcs3
ENV AWS_SHARED_CREDENTIALS_FILE=/.rcs3/.aws/credentials
ENV PS1='RCS3 Docker \w> ' 
# Entry point or command to run when the container starts
CMD /sbin/crond -n 