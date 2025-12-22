# Instance ID Parameter - Automatic Hiding

## Summary

When you have only **one instance** of Sonarr or Radarr configured, you no longer need to specify `instance_id` when using the MCP tools. The parameter is automatically hidden from the tool schema and tools will use your single instance by default.

## What Changed

### Tool Schemas (src/server.py)
- The `instance_id` parameter now only appears in tool schemas when **multiple instances** are configured
- For single-instance setups, the parameter is completely hidden
- Implementation uses a helper function `_add_instance_param()` that conditionally adds the parameter

### Tool Methods (src/tools/sonarr_tools.py & src/tools/radarr_tools.py)
- All methods now accept `instance_id: int | None = None` instead of `instance_id: int = 1`
- When `instance_id` is `None`, the tools automatically use the first available instance
- The `_get_client()` method selects the lowest numbered instance ID when none is specified

### Server Handler (src/server.py call_tool)
- Changed from `arguments.get("instance_id", 1)` to `arguments.get("instance_id")`
- Returns `None` when the parameter isn't present, which triggers automatic instance selection

## Behavior

### Single Instance (Your Current Setup)
```json
{
  "name": "sonarr_search_series",
  "inputSchema": {
    "properties": {
      "query": {"type": "string", "description": "..."}
    }
  }
}
```
**No `instance_id` parameter** - you just call the tool with the required parameters.

### Multiple Instances
```json
{
  "name": "sonarr_search_series",
  "inputSchema": {
    "properties": {
      "query": {"type": "string", "description": "..."},
      "instance_id": {"type": "integer", "description": "Sonarr instance ID (default: 1)"}
    }
  }
}
```
**Has `instance_id` parameter** - you can specify which instance to use.

## Testing

Your current configuration:
- **1 Sonarr instance** → instance_id hidden
- **1 Radarr instance** → instance_id hidden

All tools will automatically use instance ID 1 without you needing to specify it.

## Example Usage in n8n

**Before (had to specify instance_id):**
```json
{
  "query": "Breaking Bad",
  "instance_id": 1
}
```

**Now (with single instance):**
```json
{
  "query": "Breaking Bad"
}
```

Much cleaner! 🎉
