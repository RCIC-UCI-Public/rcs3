# Define the base image name
IMAGE_NAME=rcs3-rocky8

# Define tags for different versions
TAG_VERSION_SPECIFIC=8.9
TAG_LATEST=latest

# Target to build the image
build:
	docker build --no-cache -t $(IMAGE_NAME):$(TAG_VERSION_SPECIFIC) .
	docker build -t $(IMAGE_NAME):$(TAG_LATEST) .

# Target to push all built images
push:
	docker push $(IMAGE_NAME):$(TAG_VERSION_SPECIFIC)
	docker push $(IMAGE_NAME):$(TAG_LATEST)

# Make "all" the default target
        .DEFAULT_GOAL := all

# Target to clean up intermediate containers
clean:
	docker container prune -f

.PHONY: build push clean
