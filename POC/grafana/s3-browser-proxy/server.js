/**
 * S3 Browser Proxy Server
 * 
 * A Node.js Express server that provides a read-only web interface for browsing AWS S3 buckets.
 * Features include folder navigation, file metadata viewing, version history, and deleted file detection.
 * 
 * Technology Stack:
 * - Node.js with Express.js framework
 * - AWS SDK v2 for S3 operations
 * - Vanilla JavaScript (ES5/ES6) - no frameworks
 * - Static HTML/CSS frontend served by Express
 * 
 * Authentication: Supports both credential files (development) and IAM roles (production)
 */

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

// Configure base path for ALB path-based routing
const BASE_PATH = process.env.BASE_PATH || '';
console.log(`Using base path: '${BASE_PATH}'`);

// Serve static files with base path support
if (BASE_PATH) {
    app.use(BASE_PATH, express.static('public'));
} else {
    app.use(express.static('public'));
}

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

// Middleware to initialize S3 client for each request
app.use((req, res, next) => {
    try {
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        req.s3 = s3;
        req.awsCredentials = credentials;
        next();
    } catch (error) {
        console.error('Error initializing S3 client:', error);
        res.status(500).json({ error: 'Failed to initialize AWS S3 client' });
    }
});

// Helper functions for S3 operations
async function listObjectVersions(s3, params) {
    try {
        console.log(`[DEBUG] Calling listObjectVersions with params:`, params);
        const data = await s3.listObjectVersions(params).promise();
        console.log(`[DEBUG] listObjectVersions response:`, {
            versionsCount: (data.Versions || []).length,
            deleteMarkersCount: (data.DeleteMarkers || []).length,
            commonPrefixesCount: (data.CommonPrefixes || []).length,
            isTruncated: data.IsTruncated
        });
        return data;
    } catch (error) {
        console.error(`[ERROR] listObjectVersions failed:`, error.message);
        throw error;
    }
}

async function listStandardObjects(s3, params) {
    try {
        const data = await s3.listObjectsV2(params).promise();
        console.log(`[DEBUG] Response summary: ${(data.CommonPrefixes || []).length} folders, ${(data.Contents || []).length} files, isTruncated: ${data.IsTruncated}`);
        return data;
    } catch (error) {
        console.error(`[ERROR] listObjectsV2 failed:`, error.message);
        throw error;
    }
}

function processVersionGroups(versions, deleteMarkers) {
    const versionGroups = {};
    
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
    
    return versionGroups;
}

function formatAllVersionsResponse(data, versionGroups) {
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
    
    return {
        folders: data.CommonPrefixes || [],
        files: allVersions,
        isTruncated: data.IsTruncated,
        nextVersionIdMarker: data.NextVersionIdMarker,
        versionsEnabled: true
    };
}

function formatVersionInfoResponse(data, versionGroups, showDeleted) {
    // Convert to file list showing current versions (and deleted if requested)
    const filesWithVersionInfo = [];
    Object.keys(versionGroups).forEach(key => {
        const group = { versions: [], deleteMarkers: [], latest: null };
        
        // Separate versions and delete markers
        versionGroups[key].forEach(item => {
            if (item.Type === 'version') {
                group.versions.push(item);
                if (item.IsLatest) {
                    group.latest = item;
                }
            } else {
                group.deleteMarkers.push(item);
                if (item.IsLatest) {
                    group.latest = item;
                }
            }
        });
        
        const totalVersions = group.versions.length + group.deleteMarkers.length;
        const latest = group.latest;
        
        if (latest) {
            const isDeleted = latest.Type === 'deleteMarker' || latest.Size === undefined;
            
            if (!isDeleted) {
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
                // Deleted file (delete marker is latest) - only show if showDeleted is true
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
            // If isDeleted && !showDeleted, we don't add the file to the list at all
        }
    });
    
    return {
        folders: data.CommonPrefixes || [],
        files: filesWithVersionInfo,
        isTruncated: data.IsTruncated,
        nextVersionIdMarker: data.NextVersionIdMarker,
        versionsEnabled: false,
        versionInfoIncluded: true
    };
}

function formatStandardResponse(data) {
    return {
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
}

async function handleVersionListing(s3, bucketName, prefix, delimiter) {
    const params = {
        Bucket: bucketName,
        Prefix: prefix,
        Delimiter: delimiter,
        MaxKeys: 1000
    };
    
    try {
        console.log(`[DEBUG] Versioning enabled for bucket: ${bucketName}, prefix: ${prefix}`);
        const data = await listObjectVersions(s3, params);
        
        // Log raw versions for debugging
        if (data.Versions && data.Versions.length > 0) {
            console.log(`[DEBUG] Sample versions:`, data.Versions.slice(0, 2));
        }
        
        const versionGroups = processVersionGroups(data.Versions || [], data.DeleteMarkers || []);
        return formatAllVersionsResponse(data, versionGroups);
    } catch (error) {
        console.log(`[DEBUG] Falling back to standard object listing`);
        const data = await listStandardObjects(s3, params);
        return {
            folders: data.CommonPrefixes || [],
            files: data.Contents || [],
            isTruncated: data.IsTruncated,
            nextContinuationToken: data.NextContinuationToken,
            versionsEnabled: false
        };
    }
}

async function handleVersionInfoListing(s3, bucketName, prefix, delimiter, showDeleted) {
    const params = {
        Bucket: bucketName,
        Prefix: prefix,
        Delimiter: delimiter,
        MaxKeys: 1000
    };
    
    try {
        console.log(`[DEBUG] Using listObjectVersions as primary listing method`);
        const data = await listObjectVersions(s3, params);
        const versionGroups = processVersionGroups(data.Versions || [], data.DeleteMarkers || []);
        return formatVersionInfoResponse(data, versionGroups, showDeleted);
    } catch (error) {
        console.error(`[ERROR] listObjectVersions failed:`, error.message);
        const data = await listStandardObjects(s3, params);
        return formatStandardResponse(data);
    }
}

async function handleStandardListing(s3, bucketName, prefix, delimiter, continuationToken) {
    const params = {
        Bucket: bucketName,
        Prefix: prefix,
        Delimiter: delimiter,
        MaxKeys: 1000
    };
    
    // Add continuation token if provided for pagination
    if (continuationToken) {
        params.ContinuationToken = continuationToken;
        console.log(`[DEBUG] Using continuation token for pagination`);
    }
    
    const data = await listStandardObjects(s3, params);
    return formatStandardResponse(data);
}

// API Routes
// Helper function to create route path with base path
const routePath = (path) => BASE_PATH ? `${BASE_PATH}${path}` : path;

// List buckets with optional filtering
app.get(routePath('/api/buckets'), async (req, res) => {
    try {
        const data = await req.s3.listBuckets().promise();
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
app.get(routePath('/api/buckets/:bucketName/objects'), async (req, res) => {
    try {
        const { bucketName } = req.params;
        const { 
            prefix = '', 
            delimiter = '/', 
            includeVersions = 'false',
            continuationToken = ''
        } = req.query;
        
        console.log(`[DEBUG] includeVersions parameter: ${includeVersions}`);
        console.log(`[DEBUG] continuationToken: ${continuationToken ? 'present' : 'none'}`);
        
        let response;
        
        if (includeVersions === 'true') {
            // Full version listing mode
            response = await handleVersionListing(req.s3, bucketName, prefix, delimiter);
        } else {
            const useVersionsAPI = req.query.showVersionInfo === 'true';
            const showDeleted = req.query.showDeleted === 'true';
            
            if (useVersionsAPI || showDeleted) {
                // Version info mode (current versions with metadata)
                response = await handleVersionInfoListing(req.s3, bucketName, prefix, delimiter, showDeleted);
            } else {
                // Standard listing mode
                response = await handleStandardListing(req.s3, bucketName, prefix, delimiter, continuationToken);
            }
        }
        
        res.json(response);
    } catch (error) {
        console.error('Error listing objects:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get object metadata
app.get(routePath('/api/buckets/:bucketName/objects/:objectKey/metadata'), async (req, res) => {
    try {
        const { bucketName, objectKey } = req.params;
        const { versionId } = req.query;
        const decodedKey = decodeURIComponent(objectKey);
        
        const params = {
            Bucket: bucketName,
            Key: decodedKey
        };
        
        // Add version ID if provided
        if (versionId) {
            params.VersionId = versionId;
        }
        
        const data = await req.s3.headObject(params).promise();
        res.json(data);
    } catch (error) {
        console.error('Error getting object metadata:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get object versions
app.get(routePath('/api/buckets/:bucketName/objects/:objectKey/versions'), async (req, res) => {
    try {
        const { bucketName, objectKey } = req.params;
        const decodedKey = decodeURIComponent(objectKey);
        
        console.log(`[DEBUG] Getting versions for key: ${decodedKey} in bucket: ${bucketName}`);
        
        const params = {
            Bucket: bucketName,
            Prefix: decodedKey,
            MaxKeys: 1000
        };
        
        const data = await req.s3.listObjectVersions(params).promise();
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
app.get(routePath('/api/health'), (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Runtime info endpoint - detect if running on server vs locally
app.get(routePath('/api/runtime-info'), (req, res) => {
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
app.post(routePath('/api/reload-credentials'), (req, res) => {
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
