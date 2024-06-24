#!/bin/bash

# check for incomplete multipart uploads

show_all=false

if [[ "$1" == "-a" || "$1" == "--all" ]]; then
    show_all=true
fi

for B in $(aws s3api list-buckets --query "Buckets[].Name" --output text); do
    if $show_all; then
        # shows Owner and Initiator as well including ID
        UPLOADS=$(aws s3api list-multipart-uploads --bucket $B --query "Uploads[*]")
    else
        # shows Owner and Initiator as well but without ID (Initiator.ID has arn which include DisplayName)
        UPLOADS=$(aws s3api list-multipart-uploads --bucket $B --query "Uploads[].{UploadId: UploadId, Key: Key, Initiated: Initiated, StorageClass: StorageClass, Owner: Owner.DisplayName, Initiator: Initiator.DisplayName}")
    fi

    if [ "$UPLOADS" != "[]" ] && [ "$UPLOADS" != "null" ]; then
        echo "Bucket: $B"
        echo "$UPLOADS" | jq '.'
        echo
    fi
done
