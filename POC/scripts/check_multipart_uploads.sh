#!/bin/bash

# check for incomplete multipart uploads

for B in $(aws s3api list-buckets --query "Buckets[].Name" --output text); do
    UPLOADS=$(aws s3api list-multipart-uploads --bucket $B --query "Uploads[*]")
    if [ "$UPLOADS" != "[]" ] && [ "$UPLOADS" != "null" ]; then
        echo "Bucket: $B"
        echo "$UPLOADS"
        echo
    fi
done
