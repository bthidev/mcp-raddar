# New Data Extraction Tools

## Summary

Added **10 new MCP tools** for data extraction from Sonarr and Radarr, bringing the total from **8 to 18 tools**.

## New Sonarr Tools (5)

### 1. sonarr_get_quality_profiles
**Purpose**: Get available quality profiles
**Use Case**: Find quality profile IDs needed when adding new series
**Returns**:
```json
[
  {
    "id": 1,
    "name": "HD-1080p",
    "upgradeAllowed": true,
    "cutoff": "Bluray-1080p"
  }
]
```

### 2. sonarr_get_root_folders
**Purpose**: Get configured root folders
**Use Case**: Find root folder paths needed when adding new series
**Returns**:
```json
[
  {
    "id": 1,
    "path": "/tv",
    "accessible": true,
    "freeSpace": 500000000000,
    "totalSpace": 1000000000000
  }
]
```

### 3. sonarr_get_queue
**Purpose**: Get the current download queue
**Use Case**: Monitor what's currently downloading
**Parameters**:
- `page` (default: 1)
- `page_size` (default: 20)

**Returns**:
```json
{
  "records": [
    {
      "title": "Series.S01E01.1080p.WEB.x264",
      "status": "downloading",
      "size": 2500000000,
      "sizeleft": 1000000000,
      "timeleft": "00:15:30",
      "protocol": "torrent",
      "series": "Breaking Bad",
      "episode": "S01E01 - Pilot"
    }
  ],
  "totalRecords": 5
}
```

### 4. sonarr_get_calendar
**Purpose**: Get upcoming episodes
**Use Case**: See what episodes are airing soon
**Parameters**:
- `start_date` (YYYY-MM-DD, default: today)
- `end_date` (YYYY-MM-DD, default: today + 7 days)

**Returns**:
```json
[
  {
    "title": "Pilot",
    "episodeNumber": 1,
    "seasonNumber": 1,
    "airDate": "2025-12-25",
    "series": "Breaking Bad",
    "hasFile": false,
    "monitored": true
  }
]
```

### 5. sonarr_get_system_status
**Purpose**: Get system information
**Use Case**: Check Sonarr version and health
**Returns**:
```json
{
  "version": "4.0.0.1",
  "buildTime": "2024-01-01T00:00:00Z",
  "osName": "ubuntu",
  "osVersion": "22.04",
  "isLinux": true,
  "branch": "main",
  "authentication": "forms"
}
```

## New Radarr Tools (5)

### 1. radarr_get_quality_profiles
Same as Sonarr version but for movies

### 2. radarr_get_root_folders
Same as Sonarr version but for movies

### 3. radarr_get_queue
Same as Sonarr version but for movies (shows movie info instead of episode info)

### 4. radarr_get_calendar
**Purpose**: Get upcoming movie releases
**Parameters**:
- `start_date` (YYYY-MM-DD, default: today)
- `end_date` (YYYY-MM-DD, default: today + 30 days)

**Returns**:
```json
[
  {
    "title": "The Matrix",
    "year": 1999,
    "physicalRelease": "2025-01-15",
    "digitalRelease": "2025-01-01",
    "inCinemas": "2024-12-25",
    "hasFile": false,
    "monitored": true
  }
]
```

### 5. radarr_get_system_status
Same as Sonarr version but for Radarr system

## Complete Tool List (18 Total)

### Sonarr (9 tools)
1. sonarr_search_series
2. sonarr_list_series
3. sonarr_get_history
4. sonarr_add_series
5. ✨ **sonarr_get_quality_profiles** (NEW)
6. ✨ **sonarr_get_root_folders** (NEW)
7. ✨ **sonarr_get_queue** (NEW)
8. ✨ **sonarr_get_calendar** (NEW)
9. ✨ **sonarr_get_system_status** (NEW)

### Radarr (9 tools)
1. radarr_search_movies
2. radarr_list_movies
3. radarr_get_history
4. radarr_add_movie
5. ✨ **radarr_get_quality_profiles** (NEW)
6. ✨ **radarr_get_root_folders** (NEW)
7. ✨ **radarr_get_queue** (NEW)
8. ✨ **radarr_get_calendar** (NEW)
9. ✨ **radarr_get_system_status** (NEW)

## Common Use Case Workflows

### Adding a New Series/Movie
```
1. sonarr_get_quality_profiles → Get quality profile ID
2. sonarr_get_root_folders → Get root folder path
3. sonarr_search_series → Find the series
4. sonarr_add_series → Add with quality profile ID and root folder path
```

### Monitoring Downloads
```
1. sonarr_get_queue → Check current downloads
2. Repeat periodically to monitor progress
```

### Checking Upcoming Content
```
1. sonarr_get_calendar → See what's airing this week
2. radarr_get_calendar → See what movies are releasing
```

## Instance ID Behavior

Since you have only **one instance** of each service:
- ❌ `instance_id` parameter is **hidden** from all tools
- ✅ All tools automatically use your configured instance
- 🎯 Cleaner API - no need to specify instance IDs in n8n

## Technical Implementation

**Client Layer**: Added 3 new methods to each client (SonarrClient, RadarrClient):
- `get_queue()` - Fetch download queue
- `get_calendar()` - Fetch upcoming releases
- `get_system_status()` - Fetch system info

(Note: `get_quality_profiles()` and `get_root_folders()` already existed)

**Tools Layer**: Added 5 wrapper methods to each tool class (SonarrTools, RadarrTools) with:
- Optional `instance_id` parameter (automatically resolved)
- Error handling and logging
- JSON formatting for MCP responses

**Server Layer**: Registered all 10 new tools with:
- Dynamic schema generation (hides instance_id for single-instance setups)
- Tool call handlers
- Parameter validation
