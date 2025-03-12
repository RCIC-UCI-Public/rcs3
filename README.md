# rcs3
rclone to S3 for large backup
This is a set of scripts and documentation for How UCI uses rclone to backup larger servers (100+TB) to Amazon S3 Glacier Flexible Retrieval. In particular,
UCI (University of California, Irvine) plans to use these to backup large data servers in labs.

**THIS is UNDER DEVELOPMENT and SHOULD NOT BE USED UNTIL 'release'**

It utilizes some of the following features/technologies

* Object Versioning in AWS S3 to provide "snapshot-like" functionality to go back in time for restores
* AWS Life Cycle Rules to transition data from S3 to Glacier Deep Archive
* AWS Life Cycle Rules to retain versions and permanently deleted files
* Rclone itself (swiss army knife of data copy/sync)
* Convenience scripts to create: IAM Roles, S3 access Policies, service accounts
* Convenience scripts to backup data
* Convenience scripts to restore data from a point in time
* Some cost-optimization to perform daily uploads of modified data and weekly "syncs" (true-ups)
* Cost estimations for both storage capacity and ongoing API calls for backups/synchronization
* Server-side encryption of data at rest.

Logically, control of the backup storage is split into at least two for security separation

* Client: Can upload/download files. Can Delete Files (but not specific versions)
* Central Admin: Can Create Buckets, Service Accounts, IAM Roles, Apply Lifecycle rules (MFA Required)
* Deletion Admin: Can Delete Buckets, Create Lifecycle Rules, Permanently Delete Data, Permanently Delete Objects (MFA Required)


