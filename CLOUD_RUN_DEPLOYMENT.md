# 🚀 Google Cloud Run Deployment Guide - Jyotiṣa API

## 📋 Overview

This guide will help you deploy your Jyotiṣa API to Google Cloud Run for production use.

## 🛠️ Prerequisites

### 1. Google Cloud Account
- [Create a Google Cloud account](https://cloud.google.com/)
- [Set up billing](https://cloud.google.com/billing/docs/how-to/modify-project)

### 2. Install Required Tools

#### Google Cloud SDK
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

#### Docker
```bash
# macOS
brew install --cask docker

# Or download from: https://docs.docker.com/get-docker/
```

### 3. Initialize Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Initialize your project
gcloud init

# Set your project ID
gcloud config set project YOUR_PROJECT_ID
```

## 🚀 Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

1. **Edit the script configuration:**
   ```bash
   # Open deploy-cloud-run.sh and update:
   PROJECT_ID="your-actual-project-id"
   ```

2. **Run the deployment:**
   ```bash
   ./deploy-cloud-run.sh
   ```

### Option 2: Manual Deployment

1. **Enable required APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and push the Docker image:**
   ```bash
   # Build the image
   docker build -t gcr.io/YOUR_PROJECT_ID/jyotish-api .
   
   # Push to Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/jyotish-api
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy jyotish-api \
     --image gcr.io/YOUR_PROJECT_ID/jyotish-api \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --port 8080 \
     --memory 512Mi \
     --cpu 1 \
     --max-instances 10 \
     --timeout 300 \
     --concurrency 80
   ```

## 🔧 Configuration

### Environment Variables

You can set environment variables during deployment:

```bash
gcloud run services update jyotish-api \
  --update-env-vars CORS_ORIGINS="https://your-frontend.com,http://localhost:3000"
```

### Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port for the application | `8080` |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |
| `CORS_ORIGINS` | Allowed CORS origins | Localhost URLs |
| `API_KEY` | API key for authentication | None |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | None |

### Resource Configuration

| Resource | Value | Description |
|----------|-------|-------------|
| **Memory** | 512Mi | Sufficient for Swiss Ephemeris calculations |
| **CPU** | 1 | Single CPU core |
| **Max Instances** | 10 | Prevents excessive scaling |
| **Timeout** | 300s | 5 minutes for complex calculations |
| **Concurrency** | 80 | Requests per instance |

## 🌐 Domain Configuration

### Custom Domain (Optional)

1. **Map a custom domain:**
   ```bash
   gcloud run domain-mappings create \
     --service jyotish-api \
     --domain api.yourdomain.com \
     --region us-central1
   ```

2. **Update DNS records** as instructed by the command output.

### SSL Certificate

Cloud Run automatically provides SSL certificates for:
- Default domains: `https://jyotish-api-xxxxx-uc.a.run.app`
- Custom domains (after DNS verification)

## 📊 Monitoring and Logging

### View Logs
```bash
# View real-time logs
gcloud logs tail --service=jyotish-api

# View specific log entries
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=jyotish-api"
```

### Set up Monitoring

1. **Enable Cloud Monitoring:**
   ```bash
   gcloud services enable monitoring.googleapis.com
   ```

2. **Create alerts for:**
   - High error rates
   - High latency
   - Resource usage

## 🔒 Security

### IAM Permissions

Ensure your service account has minimal required permissions:

```bash
# Grant Cloud Run Invoker role (if needed)
gcloud run services add-iam-policy-binding jyotish-api \
  --member="user:your-email@domain.com" \
  --role="roles/run.invoker"
```

### API Key Authentication

If you want to require API keys:

1. **Update the deployment:**
   ```bash
   gcloud run services update jyotish-api \
     --update-env-vars API_KEY="your-secret-api-key"
   ```

2. **Update your frontend** to include the API key in requests.

## 🧪 Testing the Deployment

### Health Check
```bash
curl https://your-service-url/health
```

### API Info
```bash
curl https://your-service-url/info
```

### Panchanga Calculation
```bash
curl "https://your-service-url/v1/panchanga/precise/daily?date=2024-12-19&latitude=43.297&longitude=5.3811"
```

## 🔄 Continuous Deployment

### Using Cloud Build (Recommended)

1. **Connect your GitHub repository** to Cloud Build
2. **Use the provided `cloudbuild.yaml`**
3. **Set up triggers** for automatic deployment on push

### Manual Updates

```bash
# Build and push new image
docker build -t gcr.io/YOUR_PROJECT_ID/jyotish-api:latest .
docker push gcr.io/YOUR_PROJECT_ID/jyotish-api:latest

# Update the service
gcloud run services update jyotish-api \
  --image gcr.io/YOUR_PROJECT_ID/jyotish-api:latest
```

## 💰 Cost Optimization

### Pricing
- **CPU/Memory**: Pay per request + resource usage
- **Network**: Egress charges apply
- **Storage**: Container Registry storage costs

### Optimization Tips
1. **Set max instances** to prevent runaway costs
2. **Use appropriate memory** (512Mi is sufficient)
3. **Monitor usage** with Cloud Monitoring
4. **Set up billing alerts**

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs
gcloud builds log BUILD_ID

# Verify Dockerfile
docker build --no-cache .
```

#### 2. Runtime Errors
```bash
# Check service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=jyotish-api" --limit=50
```

#### 3. CORS Issues
- Verify CORS_ORIGINS environment variable
- Check frontend origin is included
- Test with curl to isolate frontend issues

#### 4. Memory Issues
- Increase memory allocation if needed
- Monitor memory usage in Cloud Console

### Performance Issues

#### 1. Cold Starts
- Use execution environment gen2
- Enable CPU boost
- Consider keeping warm instances

#### 2. High Latency
- Check network latency
- Optimize Swiss Ephemeris calculations
- Use caching where appropriate

## 📞 Support

### Google Cloud Support
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)

### API-Specific Issues
- Check the `/health` endpoint
- Review application logs
- Test locally first

## 🎯 Next Steps

1. **Deploy your frontend** to a hosting service
2. **Update frontend URLs** to use the new API endpoint
3. **Set up monitoring** and alerts
4. **Configure custom domain** if needed
5. **Set up CI/CD** for automatic deployments

---

**Happy deploying! 🚀**

Your Jyotiṣa API will be available at: `https://jyotish-api-xxxxx-uc.a.run.app`
