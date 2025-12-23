# Documentation Index

Quick reference to all documentation files in this repository.

## Main Documentation

### [README.md](README.md)
**Purpose**: Main project documentation
**Contents**:
- Project overview and features
- Complete list of all 18 MCP tools
- Installation instructions (local and Docker)
- Configuration guide
- Usage examples
- n8n integration guide
- Troubleshooting
- Architecture overview
- GitHub Actions CI/CD information

**Read this first** to understand what the project does and how to use it.

---

## Docker Documentation

### [DOCKER_HUB_README.md](DOCKER_HUB_README.md)
**Purpose**: Docker Hub repository description
**Contents**:
- Quick start guide for Docker users
- Environment variable reference
- Multi-instance configuration
- Docker Compose example
- Usage with n8n
- Common workflows with curl examples
- Health checks and logging

**This is what appears on Docker Hub** when someone views your image.

---

## CI/CD Documentation

### [CICD_SETUP.md](CICD_SETUP.md)
**Purpose**: Complete guide for setting up GitHub Actions pipeline
**Contents**:
- Step-by-step setup instructions
- Creating Docker Hub access tokens
- Configuring GitHub secrets
- Testing the pipeline
- Versioning strategy
- Troubleshooting common issues
- Security notes

**Read this when**: Setting up automated builds and deployments.

### [CHANGELOG.md](CHANGELOG.md)
**Purpose**: Track all project changes
**Contents**:
- Version history
- Added features
- Changed functionality
- Fixed bugs
- Breaking changes

**Automatically updated** by GitHub Actions on each release.

---

## Feature Documentation

### [NEW_TOOLS.md](NEW_TOOLS.md)
**Purpose**: Detailed documentation of the 10 new data extraction tools
**Contents**:
- Summary of new tools
- Detailed description of each tool
- Example requests and responses
- Common use case workflows
- Complete tool list (all 18 tools)

**Read this when**: Learning about the new quality profiles, root folders, queue, calendar, and system status tools.

---

## Integration Documentation

### [N8N_GUIDE.md](N8N_GUIDE.md)
**Purpose**: Complete n8n integration guide
**Contents**:
- Quick start (5 minutes)
- Connection methods (Docker network, host, remote)
- MCP Client Tool configuration
- Available tools (18 tools)
- Example prompts and workflows
- Troubleshooting common issues
- Advanced configuration

**Read this when**: Setting up n8n integration or troubleshooting n8n connectivity.

---

## Project Structure Files

### [CLAUDE.md](CLAUDE.md)
**Purpose**: Instructions for Claude Code AI assistant
**Contents**:
- Project overview
- Development commands
- Architecture details
- Configuration system
- Implementation patterns
- Testing notes

**For**: AI assistants and new developers to understand the codebase quickly.

---

## GitHub Actions Workflows

### [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)
**Purpose**: Automated Docker build and publish pipeline
**Triggers**: Version tags (v*.*.*)
**Actions**:
1. Build multi-platform Docker images
2. Push to Docker Hub with version tags
3. Update Docker Hub description
4. Generate CHANGELOG entry
5. Commit changelog back to repository

### [.github/workflows/pr-checks.yml](.github/workflows/pr-checks.yml)
**Purpose**: Code quality checks on pull requests
**Checks**:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Docker build validation

---

## Quick Reference by Use Case

### "I want to deploy this with Docker"
1. Read: [DOCKER_HUB_README.md](DOCKER_HUB_README.md)
2. Quick start: Pull image and configure with `.env` file
3. Check: [README.md](README.md) Docker Deployment section

### "I want to contribute/develop"
1. Read: [README.md](README.md) Installation and Development sections
2. Check: [CLAUDE.md](CLAUDE.md) for architecture
3. Follow: Code quality checks in [.github/workflows/pr-checks.yml](.github/workflows/pr-checks.yml)

### "I want to set up CI/CD"
1. Read: [CICD_SETUP.md](CICD_SETUP.md) completely
2. Create: Docker Hub access token
3. Configure: GitHub secrets
4. Test: Create a version tag

### "I want to understand the new tools"
1. Read: [NEW_TOOLS.md](NEW_TOOLS.md) for tool details
2. Check: [CHANGELOG.md](CHANGELOG.md) for what changed
3. Try: Example workflows in [NEW_TOOLS.md](NEW_TOOLS.md)

### "I want to use with n8n"
1. Read: [N8N_GUIDE.md](N8N_GUIDE.md) for complete integration guide
2. Quick start: Follow the 5-minute setup in N8N_GUIDE.md
3. Troubleshoot: Use the comprehensive troubleshooting section
4. Try: Example prompts and workflows with all 18 tools

### "Something is broken"
1. Check: [README.md](README.md) Troubleshooting section
2. Review: [CHANGELOG.md](CHANGELOG.md) for recent changes
3. Look: GitHub Actions logs if CI/CD related

---

## File Relationships

```
README.md (Main doc)
├── Links to: NEW_TOOLS.md (detailed tool docs)
├── Links to: CICD_SETUP.md (pipeline setup)
└── References: CHANGELOG.md (version history)

DOCKER_HUB_README.md (Docker Hub)
├── Simplified version of README.md
├── Docker-specific instructions
└── Quick start focused

CICD_SETUP.md (DevOps)
├── Uses: .github/workflows/docker-publish.yml
├── Updates: DOCKER_HUB_README.md on Docker Hub
└── Generates: CHANGELOG.md entries

NEW_TOOLS.md (Features)
├── Documents: 10 new tools added
└── Referenced by: README.md

N8N_GUIDE.md (Integration)
├── Consolidates: N8N_QUICKSTART.md + N8N_INTEGRATION.md
├── Quick start + comprehensive reference
└── Referenced by: README.md

CLAUDE.md (Developer)
├── For: AI assistants and developers
├── Details: Architecture and patterns
└── Includes: Instance ID parameter behavior
```

---

## Maintenance

### Keeping Documentation Updated

**When adding new features**:
1. Update: [README.md](README.md) Available Tools section
2. Create: Feature-specific doc (like NEW_TOOLS.md)
3. Update: [CHANGELOG.md](CHANGELOG.md) Unreleased section
4. Update: [DOCKER_HUB_README.md](DOCKER_HUB_README.md) if Docker-related

**When releasing a version**:
1. Create version tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Wait: GitHub Actions updates CHANGELOG.md and Docker Hub
4. Pull: Updated CHANGELOG.md from repository

**When changing CI/CD**:
1. Update: [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)
2. Document: [CICD_SETUP.md](CICD_SETUP.md)
3. Test: With `workflow_dispatch` before tagging

---

## Documentation Standards

- **Markdown format**: All docs use GitHub-flavored Markdown
- **Code blocks**: Use language-specific syntax highlighting
- **Examples**: Include working examples when possible
- **Links**: Use relative links between docs
- **TOC**: Long docs should have table of contents
- **Updates**: Keep examples and versions current

---

## Getting Help

If documentation is unclear or missing:
1. Check [README.md](README.md) Troubleshooting
2. Review related workflow logs in GitHub Actions
3. Check [CHANGELOG.md](CHANGELOG.md) for recent changes
4. Open an issue on GitHub with the `documentation` label
