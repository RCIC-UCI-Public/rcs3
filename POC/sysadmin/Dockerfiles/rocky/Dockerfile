# Use the latest version of Rocky Linux 8 as the base image
FROM rockylinux/rockylinux:8

# Install desired packages via yum
RUN yum -y install \
    epel-release 
RUN yum -y install \
    git \
    zip \
    vim \
    procps-ng \
    python3 \
    python3-yaml \
    python3-psutil \
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

# Get the latest version of rclone - v1.63.1 as of this writing
RUN RCLONE_VERSION=$(curl -s https://downloads.rclone.org/version.txt | awk -F'[ \t]+' '{print $2}') && \
    curl -O "https://downloads.rclone.org/$RCLONE_VERSION/rclone-$RCLONE_VERSION-linux-amd64.rpm" && \
    yum localinstall -y "rclone-$RCLONE_VERSION-linux-amd64.rpm" && \
    rm "rclone-$RCLONE_VERSION-linux-amd64.rpm"

# Set up any additional configurations if needed
# ...

# Entry point or command to run when the container starts
#CMD ["sh", "-c", "crond start && /bin/bash"]
CMD /sbin/crond -n 
