# RClone Downloader

A Python utility that downloads files from rclone remotes and optionally flattens hierarchical directory structures. This script can convert directory paths like `2011/11/birthday` into flattened names like `2011_11_birthday` for applications that don't support nested folder structures.

## Use Case

This tool is designed for downloading and organizing media collections from cloud storage services configured with rclone. It's particularly useful when you have files organized in nested folders that need to be reorganized with flattened directory structures.

## Prerequisites

- **rclone**: Must be installed and available in your system PATH
- **Python 3.6+**: Uses type hints and modern Python features
- **Configured rclone remotes**: Your cloud storage must be configured in rclone

### Setting up rclone

If you haven't configured rclone yet:

```bash
# Install rclone (varies by system)
# Ubuntu/Debian: sudo apt install rclone
# macOS: brew install rclone
# Windows: Download from https://rclone.org/downloads/

# Configure your cloud storage remote
rclone config
```

## Installation

No installation required - just download the script:

```bash
curl -O https://raw.githubusercontent.com/your-repo/rclone-unfold/main/rclone-unfold.py
```

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

**8. Copy only specific file types:**
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

**9. Move files (download and delete from remote):**
```bash
# Download and delete validated files from remote
python rclone-unfold.py dropbox "Camera Uploads" --delete-after-download -d ./photos

# Move only images with flattening
python rclone-unfold.py dropbox "Camera Uploads" -f images --flatten --delete-after-download -d ./photos
```

**10. Interactive mode for safe operations:**
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
- Files successfully deleted from remote
- Files that failed to delete (with error details)

**Flattened Operations** (when using `--flatten`):
- Original directory structure depth
- Directory name transformations applied

## Post-Operation Validation

After completing a download (not during dry-run), the script automatically validates that all expected files were successfully downloaded:

- **File Existence Check**: Verifies each file exists at the expected local path
- **Size Validation**: Compares local file size with remote file size
- **Detailed Reporting**: Shows missing files and size mismatches with specific details
- **Path Resolution**: Handles both flattened and preserved directory structures

The validation process helps ensure download integrity and identifies any files that may need to be re-downloaded.

## Remote File Deletion

When using the `--delete-after-download` option, the script performs a safe "move" operation:

1. **Download**: Files are first downloaded to the local destination
2. **Validation**: Each file is validated for existence and correct size
3. **Deletion**: Only successfully validated files are deleted from the remote

**Safety Features:**
- Files are only deleted if they pass validation (exist locally with correct size)
- Failed downloads or corrupted files remain on the remote
- Detailed reporting shows which files were deleted and which failed
- Each deletion is performed individually to ensure granular error handling

**Use Cases:**
- Migrating files from cloud storage with automatic cleanup
- Freeing up remote storage space after successful downloads
- Ensuring files are moved (not just copied) to avoid duplicates

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
Source directory: Camera Uploads
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

⚠️  About to delete 150 validated files from remote 'dropbox'
Are you sure you want to delete these files from the remote? [N/y]: n
Deletion cancelled by user. Files remain on remote.
```

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

## Performance Notes

- The script uses rclone's `--progress` flag to show transfer progress
- Large directories are processed efficiently by discovering structure first
- Dry run mode allows you to verify operations before copying

## License

MIT License - feel free to modify and distribute as needed.