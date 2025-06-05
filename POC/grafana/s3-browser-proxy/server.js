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
        const { prefix = '', delimiter = '/' } = req.query;
        
        const credentials = loadAWSCredentials();
        const s3 = initializeS3Client(credentials);
        
        if (!s3) {
            return res.status(500).json({ error: 'AWS S3 client could not be initialized' });
        }
        
        const params = {
            Bucket: bucketName,
            Prefix: prefix,
            Delimiter: delimiter,
            MaxKeys: 1000
        };
        
        const data = await s3.listObjectsV2(params).promise();
        
        // Separate folders (common prefixes) and files (contents)
        const response = {
            folders: data.CommonPrefixes || [],
            files: data.Contents || [],
            isTruncated: data.IsTruncated,
            nextContinuationToken: data.NextContinuationToken
        };
        
        res.json(response);
    } catch (error) {
        console.error('Error listing objects:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get object metadata
app.get('/api/buckets/:bucketName/objects/:objectKey/metadata', async (req, res) => {
    try {
        const { bucketName, objectKey } = req.params;
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
        
        const data = await s3.headObject(params).promise();
        res.json(data);
    } catch (error) {
        console.error('Error getting object metadata:', error);
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
