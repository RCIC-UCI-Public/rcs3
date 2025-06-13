const express = require('express');
const cors = require('cors');
const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Configure CORS
app.use(cors({
    origin: true,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json());
app.use(express.static('public'));

// Load AWS credentials from config or use EC2 IAM role
function loadAWSCredentials() {
    try {
        const configPath = path.join(__dirname, 'config', 'credentials.json');
        if (fs.existsSync(configPath)) {
            const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            console.log('Using credentials from config file');
            return config;
        }
    } catch (error) {
        console.error('Error loading credentials:', error);
    }
    
    // If no config file, return null to use EC2 IAM role
    console.log('No credentials file found, using EC2 IAM role');
    return null;
}

// Initialize AWS S3 client with credentials or EC2 IAM role
function initializeS3Client(credentials) {
    const config = {
        region: process.env.AWS_REGION || 'us-west-2'
    };
    
    if (credentials) {
        // Use provided credentials
        config.accessKeyId = credentials.accessKeyId;
        config.secretAccessKey = credentials.secretAccessKey;
        
        // Add session token if available (for temporary credentials)
        if (credentials.sessionToken) {
            config.sessionToken = credentials.sessionToken;
        }
    }
    // If no credentials provided, AWS SDK will automatically use EC2 IAM role
    
    AWS.config.update(config);
    return new AWS.S3();
}

// API Routes

// List buckets with optional filtering
app.get('/api/buckets', async (req, res) => {
    try {
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        const data = await s3.listBuckets().promise();
        let buckets = data.Buckets;
        
        // Filter buckets based on query parameter
        const { filter } = req.query;
        if (filter) {
            const allowedBuckets = filter.split(',').map(b => b.trim());
            buckets = buckets.filter(bucket => allowedBuckets.includes(bucket.Name));
        }
        
        res.json(buckets);
    } catch (error) {
        console.error('Error listing buckets:', error);
        res.status(500).json({ error: error.message });
    }
});

// List objects in bucket
app.get('/api/buckets/:bucketName/objects', async (req, res) => {
    try {
        const { bucketName } = req.params;
        const { prefix = '', delimiter = '/', includeVersions = 'false' } = req.query;
        
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        console.log(`[DEBUG] includeVersions parameter: ${includeVersions}`);
        
        if (includeVersions === 'true') {
            try {
                // Use listObjectVersions for versioning support
                console.log(`[DEBUG] Versioning enabled for bucket: ${bucketName}, prefix: ${prefix}`);
                const params = {
                    Bucket: bucketName,
                    Prefix: prefix,
                    Delimiter: delimiter,
                    MaxKeys: 1000
                };
                
                console.log(`[DEBUG] Calling listObjectVersions with params:`, params);
                const data = await s3.listObjectVersions(params).promise();
                console.log(`[DEBUG] listObjectVersions response:`, {
                    versionsCount: (data.Versions || []).length,
                    deleteMarkersCount: (data.DeleteMarkers || []).length,
                    commonPrefixesCount: (data.CommonPrefixes || []).length,
                    isTruncated: data.IsTruncated
                });
                
                // Log raw versions for debugging
                if (data.Versions && data.Versions.length > 0) {
                    console.log(`[DEBUG] Sample versions:`, data.Versions.slice(0, 2));
                }
                
                // Group versions by key and mark latest versions
                const versionGroups = {};
                const versions = data.Versions || [];
                const deleteMarkers = data.DeleteMarkers || [];
                
                // Process regular versions
                versions.forEach(version => {
                    if (!versionGroups[version.Key]) {
                        versionGroups[version.Key] = [];
                    }
                    versionGroups[version.Key].push({
                        ...version,
                        Type: 'version',
                        IsLatest: version.IsLatest
                    });
                });
                
                // Process delete markers
                deleteMarkers.forEach(marker => {
                    if (!versionGroups[marker.Key]) {
                        versionGroups[marker.Key] = [];
                    }
                    versionGroups[marker.Key].push({
                        ...marker,
                        Type: 'deleteMarker',
                        IsLatest: marker.IsLatest,
                        Size: 0 // Delete markers have no size
                    });
                });
                
                // Sort versions within each group by LastModified (newest first)
                Object.keys(versionGroups).forEach(key => {
                    versionGroups[key].sort((a, b) => new Date(b.LastModified) - new Date(a.LastModified));
                });
                
                // Flatten to array with version info
                const allVersions = [];
                Object.keys(versionGroups).forEach(key => {
                    versionGroups[key].forEach((version, index) => {
                        allVersions.push({
                            ...version,
                            VersionIndex: index,
                            TotalVersions: versionGroups[key].length
                        });
                    });
                });
                
                const response = {
                    folders: data.CommonPrefixes || [],
                    files: allVersions,
                    isTruncated: data.IsTruncated,
                    nextVersionIdMarker: data.NextVersionIdMarker,
                    versionsEnabled: true
                };
                
                res.json(response);
            } catch (versionError) {
                console.error(`[ERROR] listObjectVersions failed:`, versionError.message);
                console.log(`[DEBUG] Falling back to standard object listing`);
                
                // Fall back to standard listing
                const params = {
                    Bucket: bucketName,
                    Prefix: prefix,
                    Delimiter: delimiter,
                    MaxKeys: 1000
                };
                
                const data = await s3.listObjectsV2(params).promise();
                
                const response = {
                    folders: data.CommonPrefixes || [],
                    files: data.Contents || [],
                    isTruncated: data.IsTruncated,
                    nextContinuationToken: data.NextContinuationToken,
                    versionsEnabled: false
                };
                
                res.json(response);
            }
        } else {
            // Option 1: Use listObjectVersions as primary method to get version info efficiently
            const useVersionsAPI = req.query.showVersionInfo === 'true';
            const showDeleted = req.query.showDeleted === 'true';
            
            if (useVersionsAPI || showDeleted) {
                try {
                    console.log(`[DEBUG] Using listObjectVersions as primary listing method`);
                    const params = {
                        Bucket: bucketName,
                        Prefix: prefix,
                        Delimiter: delimiter,
                        MaxKeys: 1000
                    };
                    
                    const data = await s3.listObjectVersions(params).promise();
                    
                    // Group by key to get current versions with version counts
                    const versionGroups = {};
                    const versions = data.Versions || [];
                    const deleteMarkers = data.DeleteMarkers || [];
                    
                    // Process versions
                    versions.forEach(version => {
                        if (!versionGroups[version.Key]) {
                            versionGroups[version.Key] = { versions: [], deleteMarkers: [], latest: null };
                        }
                        versionGroups[version.Key].versions.push(version);
                        if (version.IsLatest) {
                            versionGroups[version.Key].latest = version;
                        }
                    });
                    
                    // Process delete markers
                    deleteMarkers.forEach(marker => {
                        if (!versionGroups[marker.Key]) {
                            versionGroups[marker.Key] = { versions: [], deleteMarkers: [], latest: null };
                        }
                        versionGroups[marker.Key].deleteMarkers.push(marker);
                        if (marker.IsLatest) {
                            versionGroups[marker.Key].latest = marker;
                        }
                    });
                    
                    // Convert to file list showing current versions (and deleted if requested)
                    const filesWithVersionInfo = [];
                    Object.keys(versionGroups).forEach(key => {
                        const group = versionGroups[key];
                        const totalVersions = group.versions.length + group.deleteMarkers.length;
                        const latest = group.latest;
                        
                        if (latest) {
                            if (latest.Size !== undefined) {
                                // Current non-deleted file
                                filesWithVersionInfo.push({
                                    Key: key,
                                    Size: latest.Size,
                                    LastModified: latest.LastModified,
                                    StorageClass: latest.StorageClass,
                                    ETag: latest.ETag,
                                    HasMultipleVersions: totalVersions > 1,
                                    VersionCount: totalVersions,
                                    IsDeleted: false
                                });
                            } else if (showDeleted) {
                                // Deleted file (delete marker is latest)
                                filesWithVersionInfo.push({
                                    Key: key,
                                    Size: 0,
                                    LastModified: latest.LastModified,
                                    StorageClass: 'DELETE_MARKER',
                                    ETag: latest.ETag || '',
                                    HasMultipleVersions: totalVersions > 1,
                                    VersionCount: totalVersions,
                                    IsDeleted: true,
                                    DeletedDate: latest.LastModified
                                });
                            }
                        }
                    });
                    
                    const response = {
                        folders: data.CommonPrefixes || [],
                        files: filesWithVersionInfo,
                        isTruncated: data.IsTruncated,
                        nextVersionIdMarker: data.NextVersionIdMarker,
                        versionsEnabled: false,
                        versionInfoIncluded: true
                    };
                    
                    res.json(response);
                    
                } catch (versionError) {
                    console.error(`[ERROR] listObjectVersions failed:`, versionError.message);
                    // Fall back to standard listing without version info
                    const params = {
                        Bucket: bucketName,
                        Prefix: prefix,
                        Delimiter: delimiter,
                        MaxKeys: 1000
                    };
                    
                    const data = await s3.listObjectsV2(params).promise();
                    
                    const response = {
                        folders: data.CommonPrefixes || [],
                        files: (data.Contents || []).map(file => ({
                            ...file,
                            HasMultipleVersions: false,
                            VersionCount: 1
                        })),
                        isTruncated: data.IsTruncated,
                        nextContinuationToken: data.NextContinuationToken,
                        versionsEnabled: false,
                        versionInfoIncluded: false
                    };
                    
                    res.json(response);
                }
            } else {
                // Option 2: Standard fast listing without version info
                const params = {
                    Bucket: bucketName,
                    Prefix: prefix,
                    Delimiter: delimiter,
                    MaxKeys: 1000
                };
                
                const data = await s3.listObjectsV2(params).promise();
                
                const response = {
                    folders: data.CommonPrefixes || [],
                    files: (data.Contents || []).map(file => ({
                        ...file,
                        HasMultipleVersions: false,
                        VersionCount: 1
                    })),
                    isTruncated: data.IsTruncated,
                    nextContinuationToken: data.NextContinuationToken,
                    versionsEnabled: false,
                    versionInfoIncluded: false
                };
                
                res.json(response);
            }
        }
    } catch (error) {
        console.error('Error listing objects:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get object metadata
app.get('/api/buckets/:bucketName/objects/:objectKey/metadata', async (req, res) => {
    try {
        const { bucketName, objectKey } = req.params;
        const { versionId } = req.query;
        const decodedKey = decodeURIComponent(objectKey);
        
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        const params = {
            Bucket: bucketName,
            Key: decodedKey
        };
        
        // Add version ID if provided
        if (versionId) {
            params.VersionId = versionId;
        }
        
        const data = await s3.headObject(params).promise();
        res.json(data);
    } catch (error) {
        console.error('Error getting object metadata:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get object versions
app.get('/api/buckets/:bucketName/objects/:objectKey/versions', async (req, res) => {
    try {
        const { bucketName, objectKey } = req.params;
        const decodedKey = decodeURIComponent(objectKey);
        
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        console.log(`[DEBUG] Getting versions for key: ${decodedKey} in bucket: ${bucketName}`);
        
        const params = {
            Bucket: bucketName,
            Prefix: decodedKey,
            MaxKeys: 1000
        };
        
        const data = await s3.listObjectVersions(params).promise();
        console.log(`[DEBUG] listObjectVersions for file response:`, {
            versionsCount: (data.Versions || []).length,
            deleteMarkersCount: (data.DeleteMarkers || []).length
        });
        
        // Filter to exact key matches and combine versions and delete markers
        const versions = (data.Versions || [])
            .filter(version => version.Key === decodedKey)
            .map(version => ({
                ...version,
                Type: 'version'
            }));
            
        const deleteMarkers = (data.DeleteMarkers || [])
            .filter(marker => marker.Key === decodedKey)
            .map(marker => ({
                ...marker,
                Type: 'deleteMarker',
                Size: 0 // Delete markers have no size
            }));
        
        // Combine and sort by LastModified (newest first)
        const allVersions = [...versions, ...deleteMarkers]
            .sort((a, b) => new Date(b.LastModified) - new Date(a.LastModified));
        
        console.log(`[DEBUG] Found ${allVersions.length} total versions for ${decodedKey}`);
        
        res.json(allVersions);
        
    } catch (error) {
        console.error('Error getting object versions:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Runtime info endpoint - detect if running on server vs locally
app.get('/api/runtime-info', (req, res) => {
    // Check multiple indicators that we're running on a server/EC2 instance
    const isServerHosted = process.env.NODE_ENV === 'production' || 
                          process.env.AWS_EXECUTION_ENV || 
                          process.env.EC2_INSTANCE_ID ||
                          !!process.env.AWS_CONTAINER_CREDENTIALS_RELATIVE_URI ||
                          !!process.env.AWS_CONTAINER_CREDENTIALS_FULL_URI ||
                          process.platform === 'linux' && !process.env.HOME?.includes('/Users/');
    
    const credentials = loadAWSCredentials();
    
    res.json({
        isServerHosted: isServerHosted,
        authMethod: isServerHosted ? 'iam-role' : 'credentials-file',
        features: {
            refreshBuckets: !isServerHosted, // Only available locally
            reloadCredentials: !isServerHosted // Only available locally
        },
        environment: process.env.NODE_ENV || 'development',
        hasCredentialsFile: !!credentials,
        timestamp: new Date().toISOString()
    });
});

// Reload credentials endpoint
app.post('/api/reload-credentials', (req, res) => {
    try {
        const credentials = loadAWSCredentials();
        if (credentials) {
            res.json({ success: true, message: 'Credentials reloaded successfully' });
        } else {
            res.status(500).json({ success: false, message: 'Failed to reload credentials' });
        }
    } catch (error) {
        console.error('Error reloading credentials:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`S3 Browser Proxy server running on port ${PORT}`);
    console.log(`Access the web interface at: http://localhost:${PORT}`);
    
    // Check for credentials on startup
    const credentials = loadAWSCredentials();
    if (credentials) {
        console.log('AWS credentials loaded successfully');
    } else {
        console.warn('Warning: AWS credentials not found. Please configure credentials in config/credentials.json');
    }
});

module.exports = app;
