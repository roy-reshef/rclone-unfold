# RClone Unfold - Cloud Storage Bulk Downloader & Directory Flattener

A powerful Python utility for **bulk downloading** and **organizing files** from **cloud storage** using **rclone**. Supports **Google Drive**, **Dropbox**, **OneDrive**, **AWS S3**, and 40+ other cloud providers. Features smart **directory flattening**, **bulk operations**, **file type filtering**, and **safe remote deletion**.

Perfect for **data migration**, **backup automation**, **media organization**, and **cloud storage management**.

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![rclone](https://img.shields.io/badge/Powered%20by-rclone-orange.svg)](https://rclone.org/)
[![GitHub stars](https://img.shields.io/github/stars/roy-reshef/rclone-unfold?style=social)](https://github.com/roy-reshef/rclone-unfold/stargazers)

## 🎯 Key Features

- **🔄 Bulk Cloud Downloads**: Download entire directories from 40+ cloud storage providers
- **📁 Smart Directory Flattening**: Convert nested folders into flat structures automatically  
- **🔍 File Type Filtering**: Download only images, videos, documents, or audio files
- **✅ Safe Remote Deletion**: Move files with validation and smart bulk deletion
- **🎮 Interactive Mode**: Confirmation prompts for safe operations
- **📊 Detailed Statistics**: Comprehensive reporting on operations and performance
- **🔗 Universal Cloud Support**: Works with any rclone-supported provider (Google Drive, Dropbox, OneDrive, S3, etc.)

## 💡 Use Cases

Perfect for **media archival**, **cloud storage cleanup**, **data migration**, **backup automation**, and **organizing nested photo/video collections** from cloud storage services.

## Prerequisites

- **rclone**: Must be installed and available in your system PATH
- **Python 3.6+**: Uses type hints and modern Python features
- **Configured rclone remotes**: Your cloud storage must be configured in rclone

### Setting up rclone

**About rclone**: rclone is a command-line program to manage files on cloud storage. It provides a unified interface to interact with various cloud storage providers (Google Drive, Dropbox, OneDrive, S3, etc.). The key benefit of using rclone is its abstraction of the remote storage - once configured, you can use the same commands and interface regardless of which cloud provider you're using.

If you haven't configured rclone yet:

```bash
# Install rclone (varies by system)
# Ubuntu/Debian: sudo apt install rclone
# macOS: brew install rclone
# Windows: Download from https://rclone.org/downloads/

# Configure your cloud storage remote (command line)
rclone config

# Alternative: Use the web GUI for configuration
rclone rcd --rc-web-gui
# Then open http://localhost:5572 in your browser
```

## Installation

No installation required - just download the script

## Usage

### Basic Syntax

```bash
python rclone-unfold.py <remote_name> <source_dir> [options]
```

### Command Examples

The following examples demonstrate how to use the script assuming you have configured 'dropbox' as a remote:


**1. List available rclone remotes:**
```bash
python rclone-unfold.py --show-remotes
```

**2. List top-level directories on a remote:**
```bash
python rclone-unfold.py dropbox --list-remote-top-dirs
# or using short option:
python rclone-unfold.py dropbox -l
```

**3. Preview what would be copied (dry run):**
```bash
python rclone-unfold.py dropbox "Camera Uploads" --dry-run
```

**4. Copy files preserving directory structure:**
```bash
python rclone-unfold.py dropbox "Camera Uploads" --dest-dir ./photos
# or using short option:
python rclone-unfold.py dropbox "Camera Uploads" -d ./photos
```

**5. Flatten directory structure:**
```bash
python rclone-unfold.py dropbox "Camera Uploads" --flatten -d ./photos
```

**6. Custom separator for flattened names:**
```bash
python rclone-unfold.py dropbox "Camera Uploads" --flatten --separator "-" -d ./photos
# or using short options:
python rclone-unfold.py dropbox "Camera Uploads" --flatten -s "-" -d ./photos
```

**7. Copy from specific subdirectory:**
```bash
python rclone-unfold.py dropbox "Photos/2023" --flatten -d ./2023_photos
```

**8. Copy from nested subdirectories:**
```bash
# Copy from deeply nested directory
python rclone-unfold.py dropbox "Photos/2023/vacation/europe" --flatten -d ./europe_photos

# Copy from specific album directory
python rclone-unfold.py dropbox "media/misc" -f images videos -d ./misc_media
```

**9. Copy only specific file types:**
```bash
# Copy only images
python rclone-unfold.py dropbox "Camera Uploads" --file-types images -d ./photos
# or using short options:
python rclone-unfold.py dropbox "Camera Uploads" -f images -d ./photos

# Copy images and videos
python rclone-unfold.py dropbox "Camera Uploads" -f images videos -d ./media

# Copy all media types
python rclone-unfold.py dropbox "Camera Uploads" -f images videos audio -d ./media
```

**10. Move files (download and delete from remote):**
```bash
# Download and delete validated files from remote
python rclone-unfold.py dropbox "Camera Uploads" --delete-after-download -d ./photos

# Move only images with flattening
python rclone-unfold.py dropbox "Camera Uploads" -f images --flatten --delete-after-download -d ./photos
```

**11. Interactive mode for safe operations:**
```bash
# Interactive dry run with confirmation prompts
python rclone-unfold.py dropbox "Camera Uploads" --dry-run -i

# Interactive move operation with confirmations
python rclone-unfold.py dropbox "Camera Uploads" --delete-after-download -i -d ./photos
```

### Complete Example Workflow

```bash
# 1. Check your configured remotes
python rclone-unfold.py --show-remotes

# 2. Browse top-level directories on your remote
python rclone-unfold.py dropbox -l

# 3. Do a dry run to see what will happen
python rclone-unfold.py dropbox "Camera Uploads" --flatten --dry-run

# 4. Execute the actual copy
python rclone-unfold.py dropbox "Camera Uploads" --flatten -d ~/media

# 5. Copy only photos and videos with flattening
python rclone-unfold.py dropbox "Camera Uploads" -f images videos --flatten -d ~/media
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `remote_name` | Name of the rclone remote (e.g., 'dropbox') | Required |
| `source_dir` | Source directory to copy from | Required |
| `-d`, `--dest-dir` | Local destination directory | `~/Downloads` |
| `--flatten` | Flatten directory structure | False |
| `-s`, `--separator` | Character for flattening directory names | `_` |
| `--dry-run` | Preview operations without copying | False |
| `--show-remotes` | Display configured remotes and exit | False |
| `-l`, `--list-remote-top-dirs` | List top-level directories on remote and exit | False |
| `-f`, `--file-types` | Filter by file types: images, videos, docs, audio | All files |
| `--delete-after-download` | Delete files from remote after successful validation | False |
| `-i`, `--interactive` | Interactive mode with confirmation prompts | False |

## File Type Filtering

The `--file-types` (or `-f`) option allows you to filter which files are copied based on their extensions:

- **images**: Common image formats (jpg, png, gif, bmp, tiff, webp, heic, raw formats, etc.)
- **videos**: Video formats (mp4, avi, mov, mkv, webm, etc.)
- **docs**: Document formats (pdf, doc, docx, txt, csv, etc.)
- **audio**: Audio formats (mp3, wav, flac, aac, ogg, etc.)

You can specify multiple types: `--file-types images videos` or `-f images videos` will copy both images and videos.

## Statistics Reporting

The script automatically provides comprehensive statistics at the end of each operation:

**File Statistics:**
- Total files found/copied
- Files by type (images, videos, docs, audio)
- Total data size (MB/GB)
- Number of directories processed

**Performance Statistics:**
- Execution time

**Filter Statistics** (when using `--file-types`):
- Files included by type filters
- Files excluded by type filters
- List of excluded file paths (up to 20 files shown)

**Operation Statistics** (actual runs only):
- Files successfully copied vs failed
- Files skipped (already exist, etc.)
- Directories created

**Validation Results** (actual runs only):
- Files validated for existence and size
- Missing files (with paths)
- Files with size mismatches (with details)

**Deletion Results** (when using `--delete-after-download`):
- **Bulk Deletion**: Shows when entire directory was deleted
- **Individual Deletion**: Files successfully deleted vs failed
- **Detailed Error Reporting**: Failed deletions with specific error messages
- **Path Information**: Exact remote paths that were affected

**Flattened Operations** (when using `--flatten`):
- Original directory structure depth
- Directory name transformations applied

## Post-Operation Validation

After completing a download (not during dry-run), the script automatically validates that all expected files were successfully downloaded:

- **File Existence Check**: Verifies each file exists at the expected local path
- **Size Validation**: Compares local file size with remote file size
- **Detailed Reporting**: Shows missing files and size mismatches with specific details
- **Path Resolution**: Handles both flattened and preserved directory structures
- **Nested Directory Support**: Correctly validates files from any source directory depth (e.g., `media/misc`, `Photos/2023/vacation/europe`)

The validation process helps ensure download integrity and identifies any files that may need to be re-downloaded. This is especially important when working with nested source directories to ensure all files were placed in the correct local paths.

## Remote File Deletion

When using the `--delete-after-download` option, the script performs a safe "move" operation with intelligent deletion strategies:

1. **Download**: Files are first downloaded to the local destination
2. **Validation**: Each file is validated for existence and correct size
3. **Smart Deletion**: The script chooses the most efficient deletion method

### Smart Deletion Logic

**Bulk Directory Deletion (Optimal):**
- **When**: All files downloaded successfully + No files excluded by filters + No validation failures
- **Method**: Uses `rclone purge` to delete the entire source directory in one operation
- **Benefits**: Much faster than individual file deletion, cleaner remote cleanup
- **Example**: Downloading all 449 files from `media/misc` → deletes entire `media/misc` directory

**Individual File Deletion (Selective):**
- **When**: Some files were excluded, failed validation, or download errors occurred
- **Method**: Deletes only successfully validated files one by one
- **Benefits**: Precise cleanup, preserves files that weren't downloaded
- **Example**: Downloading only images (excluding videos) → deletes only the downloaded image files

### Deletion Warning Messages

**Bulk Deletion Warning:**
```
⚠️  DELETION WARNING ⚠️
All 449 files were successfully downloaded and validated.
About to delete the entire directory:
Remote: dropbox:media/misc
This will remove the directory and all its contents from the remote.
This action cannot be undone!
```

**Individual Deletion Warning:**
```
⚠️  DELETION WARNING ⚠️
About to delete 422 validated files from:
Remote: dropbox:media/misc
Note: 20 files were excluded by filters and will remain.
Only successfully validated files will be deleted individually.
This action cannot be undone!
```

**Safety Features:**
- Files are only deleted if they pass validation (exist locally with correct size)
- Failed downloads or corrupted files remain on the remote
- Clear warnings show exactly which remote path will be affected
- Automatic fallback to individual deletion if bulk deletion fails
- Interactive mode provides confirmation before any deletion

**Use Cases:**
- **Complete Migration**: Download entire directories and remove them from remote
- **Selective Cleanup**: Download specific file types while preserving others
- **Storage Management**: Free up remote space after successful downloads
- **Data Archival**: Move files from cloud storage to local archives

## Interactive Mode

Interactive mode (`-i` or `--interactive`) adds safety prompts at critical decision points:

**Confirmation Points:**
1. **After Configuration Display**: Shows all program settings and asks for confirmation to proceed
2. **Before Remote Deletion**: If `--delete-after-download` is used, prompts before actually deleting files from remote

**Benefits:**
- **Safety**: Prevents accidental operations by requiring explicit confirmation
- **Review**: Allows you to verify settings before execution
- **Control**: Gives you final say before destructive operations like deletion
- **Learning**: Helps understand what the script will do step by step

**User Experience:**
- Press Enter to accept default (usually "yes" for proceed, "no" for deletion)
- Type 'y' or 'yes' to confirm, 'n' or 'no' to cancel
- Ctrl+C to exit at any time
- Clear feedback on what action is being requested

**Example Session:**
```
PROGRAM CONFIGURATION
==================================================
Remote name: dropbox
Source directory: media/misc
Destination directory: /home/user/photos
Flatten directories: Yes
Directory separator: '_'
File types filter: images, videos
Dry run mode: No
Delete after download: Yes
Interactive mode: Yes
==================================================

Do you want to proceed with these settings? [Y/n]: y

[... operation proceeds ...]

⚠️  DELETION WARNING ⚠️
All 449 files were successfully downloaded and validated.
About to delete the entire directory:
Remote: dropbox:media/misc
This will remove the directory and all its contents from the remote.
This action cannot be undone!
Are you sure you want to delete from the remote? [N/y]: n
Deletion cancelled by user. Files remain on remote.
```

## Nested Source Directory Support

The script fully supports nested source directories at any depth level:

**Supported Path Formats:**
```bash
# Top-level directory
python rclone-unfold.py dropbox "Photos" -d ./photos

# Single-level nested
python rclone-unfold.py dropbox "Photos/2023" -d ./2023_photos

# Multi-level nested
python rclone-unfold.py dropbox "Photos/2023/vacation/europe" -d ./europe_trip

# Complex nested paths
python rclone-unfold.py dropbox "media/archives/family/birthdays/2023" -d ./family_2023
```

**How It Works:**
1. **Path Recognition**: The script treats the entire path as a source directory, not individual segments
2. **File Discovery**: Uses `rclone lsf -R` to recursively find all files within the nested path
3. **Structure Preservation**: Maintains subdirectory relationships within the specified source
4. **Validation**: Correctly validates files based on their actual download locations

**Example with `media/misc`:**
- **Source**: `dropbox:media/misc` (contains 449 files directly)
- **Flattened Result**: All files go to `{dest_dir}/misc/`
- **Preserved Result**: Files maintain structure relative to `misc`

This enhancement allows you to work with any organizational structure in your cloud storage, from simple top-level folders to deeply nested archives.

## How Directory Flattening Works

When `--flatten` is enabled:

- **Original structure:**
  ```
  Photos/
  ├── 2023/
  │   ├── 01_January/
  │   │   └── vacation/
  │   │       ├── IMG_001.jpg
  │   │       └── IMG_002.jpg
  │   └── 02_February/
  │       └── birthday/
  │           └── IMG_003.jpg
  ```

- **Flattened result:**
  ```
  photos/
  ├── 2023_01_January_vacation/
  │   ├── IMG_001.jpg
  │   └── IMG_002.jpg
  └── 2023_02_February_birthday/
      └── IMG_003.jpg
  ```

## Error Handling

The script includes comprehensive error handling:
- Validates rclone installation
- Checks for valid remote configurations
- Handles subprocess errors gracefully
- Provides clear error messages

## Troubleshooting

**"rclone command not found"**
- Ensure rclone is installed and in your PATH
- Try `rclone version` to verify installation

**"No remotes configured"**
- Run `rclone config` to set up your cloud storage remote
- Use `--show-remotes` to verify configuration

**"No source directories found"**
- Check that the source directory exists and contains files
- Verify the remote name and path are correct
- For nested paths like `media/misc`, ensure the full path exists on the remote
- Use `--list-remote-top-dirs` to browse available directories

**"Files missing during validation"**
- This was a known issue with nested source directories (now fixed)
- Ensure you're using the latest version of the script
- Validation now correctly handles nested paths like `media/misc/file.jpg`

## Performance Notes

- The script uses rclone's `--progress` flag to show transfer progress
- Large directories are processed efficiently by discovering structure first
- Dry run mode allows you to verify operations before copying
- **Smart Deletion**: When all files are downloaded successfully, uses bulk directory deletion (`rclone purge`) which is much faster than deleting hundreds of files individually
- **Nested Path Handling**: Efficiently processes deeply nested source directories without scanning unnecessary parent directories

## License

Business Source License 1.1 - free for non-production use. Will become Apache 2.0 on 2029-07-19. See [LICENSE](LICENSE) for details.