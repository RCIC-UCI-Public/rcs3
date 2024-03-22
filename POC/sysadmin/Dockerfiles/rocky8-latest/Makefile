# Define the repo name
REPO_NAME=rcs3uci

# Define the base image name
IMAGE_NAME=rcs3-rocky8

# Define tags for different versions
TAG_VERSION_SPECIFIC=8.9
TAG_LATEST=latest

# Target to build the image - once
build:
	docker build --no-cache .

# Target to tag & push images - twice - using version specific and latest tag
push:
	docker tag $(IMAGE_NAME):$(TAG_VERSION_SPECIFIC) $(REPO_NAME)/$(IMAGE_NAME):$(TAG_VERSION_SPECIFIC)
	docker push $(REPO_NAME)/$(IMAGE_NAME):$(TAG_VERSION_SPECIFIC)
	docker tag $(IMAGE_NAME):$(TAG_VERSION_SPECIFIC) $(REPO_NAME)/$(IMAGE_NAME):$(TAG_LATEST)
	docker push $(REPO_NAME)/$(IMAGE_NAME):$(TAG_LATEST)

all: build push

# Target to clean up intermediate containers
clean:
	docker container prune -f

# Make "all" the default target
.DEFAULT_GOAL := all

.PHONY: build push clean all
