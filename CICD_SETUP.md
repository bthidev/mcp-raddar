# CI/CD Pipeline Setup Guide

This guide explains how to set up the automated CI/CD pipeline for building Docker images and updating Docker Hub.

## Overview

The pipeline automatically:
1. ✅ Builds Docker images for multiple platforms (amd64, arm64)
2. ✅ Pushes to Docker Hub with proper version tags
3. ✅ Updates Docker Hub repository description
4. ✅ Generates and commits CHANGELOG.md entries
5. ✅ Triggers on version tags (e.g., `v1.0.0`)

## Prerequisites

1. Docker Hub account
2. GitHub repository
3. GitHub Actions enabled (default on public repos)

## Setup Steps

### 1. Create Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/)
2. Click your profile → **Account Settings**
3. Navigate to **Security** → **Access Tokens**
4. Click **New Access Token**
5. Name it: `github-actions-mcp-raddar`
6. Permissions: **Read, Write, Delete**
7. Click **Generate** and **copy the token** (you won't see it again!)

### 2. Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these two secrets:

**Secret 1: DOCKERHUB_USERNAME**
- Name: `DOCKERHUB_USERNAME`
- Value: Your Docker Hub username (e.g., `yourname`)

**Secret 2: DOCKERHUB_TOKEN**
- Name: `DOCKERHUB_TOKEN`
- Value: The access token you created in step 1

### 3. Verify Workflow File

The workflow is located at `.github/workflows/docker-publish.yml`

It triggers on:
- **Version tags**: `v*.*.*` (e.g., `v1.0.0`, `v2.1.3`)
- **Manual dispatch**: Can be triggered manually from GitHub Actions tab

### 4. Test the Pipeline

#### Option A: Create a Version Tag (Recommended)

```bash
# Make sure you're on the main branch
git checkout master  # or main

# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

#### Option B: Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. Click **Build and Push Docker Image** workflow
3. Click **Run workflow** dropdown
4. Select branch and click **Run workflow**

### 5. Monitor the Pipeline

1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. Watch the progress of each step:
   - ✅ Checkout code
   - ✅ Set up QEMU (for multi-platform builds)
   - ✅ Set up Docker Buildx
   - ✅ Login to Docker Hub
   - ✅ Extract metadata
   - ✅ Build and push Docker image
   - ✅ Update Docker Hub description
   - ✅ Generate changelog
   - ✅ Update CHANGELOG.md
   - ✅ Commit and push changelog

## What Gets Created

### On Docker Hub

After a successful pipeline run, your Docker Hub repository will have:

**Tags:**
- `1.0.0` - Full semantic version
- `1.0` - Major.minor version
- `latest` - Latest stable release

**Description:**
- Automatically updated from `DOCKER_HUB_README.md`
- Shows all 18 tools, usage examples, and configuration

### In Your Repository

**CHANGELOG.md:**
- Automatically updated with new version entry
- Lists all commits since previous tag
- Includes commit hashes for reference
- Committed back to the repository by GitHub Actions bot

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (v2.0.0): Incompatible API changes
- **MINOR** version (v1.1.0): New functionality, backwards compatible
- **PATCH** version (v1.0.1): Bug fixes, backwards compatible

### Example Release Workflow

```bash
# 1. Make your changes
git add .
git commit -m "feat: add new awesome feature"
git push origin master

# 2. Create and push a version tag
git tag v1.1.0
git push origin v1.1.0

# 3. Wait for GitHub Actions to complete (~5-10 minutes)

# 4. Pull the updated CHANGELOG.md
git pull origin master
```

## Pipeline Output

### Successful Run

```
✅ Docker image built for linux/amd64 and linux/arm64
✅ Pushed to Docker Hub:
   - yourname/mcp-raddar:1.0.0
   - yourname/mcp-raddar:1.0
   - yourname/mcp-raddar:latest
✅ Docker Hub description updated
✅ CHANGELOG.md generated and committed
```

### Docker Hub Tags

Users can pull with:
```bash
# Specific version
docker pull yourname/mcp-raddar:1.0.0

# Major.minor version
docker pull yourname/mcp-raddar:1.0

# Latest stable
docker pull yourname/mcp-raddar:latest
```

## Troubleshooting

### Pipeline Fails at "Login to Docker Hub"

**Problem**: Invalid credentials

**Solution**:
1. Verify `DOCKERHUB_USERNAME` is your Docker Hub username (not email)
2. Regenerate Docker Hub access token
3. Update `DOCKERHUB_TOKEN` secret in GitHub

### Pipeline Fails at "Update Docker Hub Description"

**Problem**: Repository doesn't exist or token lacks permissions

**Solution**:
1. Create the repository on Docker Hub first (it can be empty)
2. Ensure access token has **Write** permissions
3. Repository name should match: `DOCKERHUB_USERNAME/mcp-raddar`

### Pipeline Fails at "Push changelog"

**Problem**: GitHub Actions doesn't have permission to push

**Solution**:
1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Click **Save**

### Multi-platform Build is Slow

**Explanation**: Building for both amd64 and arm64 takes longer (~5-10 minutes)

**Options**:
- This is normal and ensures compatibility across platforms
- To speed up, remove `linux/arm64` from platforms (line 39 in workflow)

## Customization

### Change Docker Hub Repository Name

Edit `.github/workflows/docker-publish.yml` line 33:
```yaml
images: ${{ secrets.DOCKERHUB_USERNAME }}/YOUR-REPO-NAME
```

### Add More Platforms

Edit `.github/workflows/docker-publish.yml` line 39:
```yaml
platforms: linux/amd64,linux/arm64,linux/arm/v7
```

### Disable Automatic Changelog

Remove or comment out lines 59-111 in the workflow file.

### Change Trigger Pattern

Edit lines 4-6 in the workflow file:
```yaml
on:
  push:
    tags:
      - 'v*.*.*'        # Matches v1.0.0, v2.1.3, etc.
      - 'release-*'     # Also match release-1.0.0
```

## Security Notes

- ✅ **DOCKERHUB_TOKEN** is stored as an encrypted secret
- ✅ Token is never exposed in logs or outputs
- ✅ Token only has repository-level access (not account-level)
- ✅ Can be revoked anytime from Docker Hub settings
- ✅ GitHub Actions runs in isolated environments

## Next Steps

After setup:
1. ✅ Make your first release with `git tag v1.0.0 && git push origin v1.0.0`
2. ✅ Monitor the GitHub Actions run
3. ✅ Verify image appears on Docker Hub
4. ✅ Test pulling the image: `docker pull yourname/mcp-raddar:latest`
5. ✅ Check CHANGELOG.md was updated in your repository

## Support

If you encounter issues:
1. Check the **Actions** tab for detailed error logs
2. Verify all secrets are correctly configured
3. Ensure Docker Hub repository exists
4. Check GitHub repository permissions for Actions
