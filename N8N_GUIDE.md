# n8n Integration Guide for MCP Raddar

Complete guide for integrating MCP Raddar with n8n - from quick start to advanced configuration.

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Connection Methods](#connection-methods)
4. [Workflow Setup](#workflow-setup)
5. [Available Tools](#available-tools)
6. [Example Prompts](#example-prompts)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### 🚀 Your MCP Server is Ready!

**Server URL**: `http://mcp-raddar:8000/mcp`
**Status**: ✅ Healthy and Running
**Protocol**: Streamable HTTP (MCP 2025-03-26+)
**Network**: `media`

### Step 1: Connect n8n to the Media Network

Add this to your n8n `docker-compose.yml`:

```yaml
services:
  n8n:
    # ... your existing config ...
    networks:
      - media  # Add this line

networks:
  media:
    external: true  # Add this section
```

Then restart n8n:
```bash
docker-compose down
docker-compose up -d
```

### Step 2: Configure MCP Client Tool in n8n

In your n8n workflow:

1. Add **MCP Client Tool** node (under AI > Tools)
2. Set these values:
   - **Endpoint URL**: `http://mcp-raddar:8000/mcp`
   - **Server Transport**: `streamable-http`
3. Click "Test Connection" - should show 18 tools

### Step 3: Add a Better Chat Model

⚠️ **CRITICAL**: Replace `ministral-3b` with a better model!

**Recommended models:**
- `openai/gpt-4o-mini` ✅ Best value
- `openai/gpt-4o` ✅ Most reliable
- `anthropic/claude-3-5-sonnet` ✅ Excellent
- `mistralai/mistral-large-2407` ✅ Good

**Don't use:**
- `ministral-3b` ❌ Too small, will fail

Update your OpenRouter Chat Model node with one of the above.

### Step 4: Test Your Setup

Try this prompt in your workflow:

```
Search for Breaking Bad
```

**Expected response:**
```json
[
  {
    "title": "Breaking Bad",
    "year": 2008,
    "tvdbId": 81189,
    "overview": "...",
    "seasons": 6
  }
]
```

### Available Commands

Your bot can now handle these requests:

#### TV Series (Sonarr)
- "Search for [series name]"
- "List my TV shows"
- "Add [series name] to Sonarr"
- "What's downloading?"
- "What's coming up this week?"

#### Movies (Radarr)
- "Search for [movie name]"
- "List my movies"
- "Add [movie name] to Radarr"
- "Show movie download queue"
- "What movies are coming soon?"

#### Configuration
- "Get quality profiles"
- "Show root folders"
- "Get system status"

🎉 **You're ready to go!**

---

## Prerequisites

Before setting up n8n integration, ensure you have:

- Docker and Docker Compose installed
- n8n running (preferably in Docker)
- MCP Raddar server configured and running

## Server Configuration

The MCP server is already configured for n8n HTTP Streamable integration:

- **Protocol**: Streamable HTTP (MCP 2025-03-26+)
- **Port**: 8000
- **Endpoint**: `/mcp`
- **Network**: `media`
- **Session Management**: Enabled via MCP-Session-Id header

---

## Connection Methods

Choose the connection method that matches your setup:

### Method 1: n8n in Same Docker Network (Recommended)

If n8n is running in Docker, add it to the `media` network to enable container-to-container communication.

#### Update your n8n docker-compose.yml:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    # ... your existing n8n configuration ...
    networks:
      - n8n-network  # Your existing network
      - media        # Add this line
    # ... rest of config ...

networks:
  n8n-network:
    # Your existing network config
  media:
    external: true  # Reference the external media network
```

#### n8n MCP Client Tool Configuration:

- **Endpoint URL**: `http://mcp-raddar:8000/mcp`
- **Server Transport**: `streamable-http`

### Method 2: n8n on Host Machine

If n8n is running directly on your host machine (not in Docker):

#### n8n MCP Client Tool Configuration:

- **Endpoint URL**: `http://localhost:8000/mcp`
- **Server Transport**: `streamable-http`

### Method 3: n8n on Different Host

If n8n is on a different machine on your network:

#### n8n MCP Client Tool Configuration:

- **Endpoint URL**: `http://YOUR_SERVER_IP:8000/mcp`
- **Server Transport**: `streamable-http`

Replace `YOUR_SERVER_IP` with the IP address of the machine running MCP Raddar.

---

## Workflow Setup

### 1. Add MCP Client Tool Node

In your n8n workflow:

1. Add a new **MCP Client** node (under AI > Tools)
2. Configure the connection:
   - **Endpoint URL**: See connection methods above
   - **Server Transport**: `streamable-http`
3. Click "Test Connection" to verify

### 2. Connect to AI Agent

1. Add an **AI Agent** node
2. Connect your **Chat Model** (OpenAI, Anthropic, etc.)
3. Connect the **MCP Client Tool** to the AI Agent
4. **IMPORTANT**: Use a capable model for function calling:
   - ✅ `gpt-4o-mini` (OpenAI) - Best value
   - ✅ `gpt-4o` (OpenAI) - Most reliable
   - ✅ `claude-3-5-sonnet` (Anthropic) - Excellent
   - ✅ `mistral-large` (Mistral) - Good
   - ❌ `ministral-3b` (Mistral) - Too small, will fail

### 3. Example Workflow Structure

```
Telegram/Webhook Trigger
    ↓
AI Agent (with MCP Tools)
    ↓
Response Output
```

---

## Available Tools

The MCP server provides 18 tools:

### Sonarr Tools (9)

| Tool | Description |
|------|-------------|
| `sonarr_search_series` | Search for TV series |
| `sonarr_list_series` | List all series in library |
| `sonarr_add_series` | Add new series |
| `sonarr_get_history` | Get download history |
| `sonarr_get_queue` | Get download queue |
| `sonarr_get_calendar` | Get upcoming episodes |
| `sonarr_get_quality_profiles` | List quality profiles |
| `sonarr_get_root_folders` | List root folders |
| `sonarr_get_system_status` | Get system info |

### Radarr Tools (9)

| Tool | Description |
|------|-------------|
| `radarr_search_movies` | Search for movies |
| `radarr_list_movies` | List all movies in library |
| `radarr_add_movie` | Add new movie |
| `radarr_get_history` | Get download history |
| `radarr_get_queue` | Get download queue |
| `radarr_get_calendar` | Get upcoming releases |
| `radarr_get_quality_profiles` | List quality profiles |
| `radarr_get_root_folders` | List root folders |
| `radarr_get_system_status` | Get system info |

---

## Example Prompts

Once configured, try these prompts in your n8n workflow:

### Basic Queries
```
"Search for Breaking Bad"
"List all my TV series"
"What movies do I have?"
"Show me the download queue"
"What's coming up this week?"
"Get quality profiles for Sonarr"
```

### Advanced Queries
```
"Search for Inception and add it to Radarr"
"What TV shows are airing this week?"
"Show me the quality profiles and root folders"
"Get the download history for the last 24 hours"
```

---

## Troubleshooting

### Connection Error: "404 Not Found"

**Problem**: n8n can't find the endpoint.

**Solutions**:
- Check endpoint URL is exactly: `http://mcp-raddar:8000/mcp` (with `/mcp`)
- Verify n8n is on the `media` network
- Try `http://localhost:8000/mcp` if n8n is on host

### Connection Error: "Connection Refused"

**Problem**: n8n can't reach the server.

**Solutions**:
- Ensure MCP server is running: `docker ps | grep mcp-raddar`
- Check server logs: `docker-compose logs mcp-raddar`
- Verify port 8000 is exposed: `docker-compose ps`
- Check firewall rules if on different hosts
- Make sure n8n is on the `media` network

### Error: "Failed to parse tool arguments"

**Problem**: LLM model is too small for function calling.

**Solution**: Upgrade to a larger model (see AI Agent setup above).

### Tools Not Appearing

**Problem**: MCP client can't list tools.

**Solutions**:
- Check server logs for errors: `docker-compose logs mcp-raddar`
- Verify Sonarr/Radarr credentials are correct
- Test connectivity: `curl http://localhost:8000/mcp`

### Healthcheck Failing

**Problem**: Docker healthcheck shows unhealthy.

**Solutions**:
- Check server logs: `docker-compose logs mcp-raddar`
- Verify port 8000 is accessible inside container
- Restart container: `docker-compose restart mcp-raddar`

---

## Advanced Configuration

### Verification

#### Check Server Health

```bash
# Check if container is running
docker ps | grep mcp-raddar

# Check container health
docker-compose ps

# View logs
docker-compose logs -f mcp-raddar

# Test endpoint manually
curl http://localhost:8000/mcp
```

#### Test from n8n

1. Create a simple workflow with:
   - Manual Trigger
   - AI Agent with MCP Client Tool
   - Chat Model (gpt-4o-mini recommended)
2. Execute with prompt: "List my series"
3. Should return JSON with your series list

### Performance Tips

1. **Use appropriate LLM models**: Smaller models (< 7B) struggle with function calling
2. **Cache responses**: Use n8n's cache node for repeated queries
3. **Batch operations**: When possible, use list operations instead of multiple searches
4. **Monitor logs**: Keep an eye on `docker-compose logs` for API rate limiting

### Security Notes

- API keys are stored in environment variables
- Consider using Docker secrets for production
- Limit network exposure (don't expose port 8000 publicly)
- Use HTTPS reverse proxy for production deployments

### Example n8n Workflow JSON

Save this as a starting point:

```json
{
  "nodes": [
    {
      "parameters": {
        "endpointUrl": "http://mcp-raddar:8000/mcp",
        "serverTransport": "streamable-http"
      },
      "type": "@n8n/n8n-nodes-langchain.mcpClientTool",
      "name": "MCP Raddar",
      "position": [500, 300]
    },
    {
      "parameters": {
        "model": "gpt-4o-mini",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "name": "OpenAI Chat",
      "position": [300, 200]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "={{ $json.query }}"
      },
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent",
      "position": [300, 300]
    }
  ]
}
```

---

## Support

For issues:
1. Check server logs: `docker-compose logs mcp-raddar`
2. Verify configuration in `docker-compose.yml`
3. Test with the included `test_mcp_server.py` script
4. Open an issue on GitHub with logs and configuration

This will get you started with a comprehensive MCP integration in n8n!
