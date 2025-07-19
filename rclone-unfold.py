import argparse
import subprocess
import sys
import json
import os
import time
from pathlib import Path
from typing import List, NamedTuple, Set, Optional, Dict

# File type mappings
FILE_TYPE_MAPPINGS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico', '.heic', '.heif', '.raw', '.dng', '.cr2', '.nef', '.arw'],
    'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp', '.ogv', '.ts', '.mts', '.m2ts', '.vob', '.asf', '.rm', '.rmvb'],
    'docs': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp', '.pages', '.numbers', '.key', '.csv', '.epub'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.au', '.ra', '.amr', '.3ga', '.mka']
}

class Statistics(NamedTuple):
    total_files: int
    files_by_type: Dict[str, int]
    total_size_bytes: int
    directories_processed: int
    execution_time: float
    files_included: int
    files_excluded: int
    files_copied: int
    files_failed: int
    files_skipped: int
    directories_created: int
    max_depth: int
    transformations_applied: int

class ScriptArgs(NamedTuple):
    remote_name: str
    source_dir: str
    dest_dir: Path
    flatten: bool
    separator: str
    dry_run: bool
    show_remotes: bool
    list_remote_top_dirs: bool
    file_types: Optional[List[str]]
    delete_after_download: bool
    interactive: bool

def prompt_user_confirmation(message: str, default_response: str = "y") -> bool:
    """Prompts user for confirmation and returns True if they agree to continue."""
    valid_responses = {"y", "yes", "n", "no"}
    
    while True:
        try:
            response = input(f"{message} [{default_response.upper()}/n]: ").strip().lower()
            
            # Use default if user just presses Enter
            if not response:
                response = default_response.lower()
            
            if response in valid_responses:
                return response in {"y", "yes"}
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except EOFError:
            print("\n\nOperation cancelled.")
            sys.exit(1)

def check_rclone_exists():
    """Checks if rclone is installed and in the system's PATH."""
    try:
        subprocess.run(["rclone", "version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("Error: 'rclone' command not found. Is rclone installed and in your PATH?", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error checking rclone version: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def show_remotes():
    """Displays the configured rclone remotes and their types."""
    print("--- Configured rclone Remotes ---")
    try:
        result = subprocess.run(
            ["rclone", "config", "dump"],
            capture_output=True,
            text=True,
            check=True
        )
        config = json.loads(result.stdout)
        if not config:
            print("No remotes configured.")
            sys.exit(0)

        max_name_len = max(len(name) for name in config.keys()) if config else 0
        max_type_len = max(len(data.get("type", "")) for data in config.values()) if config else 0

        print(f"{'Name'.ljust(max_name_len)}   {'Type'.ljust(max_type_len)}")
        print(f"{'===='.ljust(max_name_len)}   {'===='.ljust(max_type_len)}")

        for name, data in sorted(config.items()):
            remote_type = data.get("type", "unknown")
            print(f"{name.ljust(max_name_len)}   {remote_type.ljust(max_type_len)}")

    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error parsing rclone configuration: {e}", file=sys.stderr)

    sys.exit(0)

def list_remote_top_dirs(remote_name: str):
    """Lists top-level directories on the specified remote."""
    print(f"--- Top-level directories on remote '{remote_name}' ---")
    try:
        result = subprocess.run(
            ["rclone", "lsf", f"{remote_name}:", "--dirs-only"],
            capture_output=True,
            text=True,
            check=True
        )
        dirs = result.stdout.strip().split('\n')
        if not dirs or all(d == '' for d in dirs):
            print("No directories found.")
            sys.exit(0)

        # Remove trailing slashes and sort
        clean_dirs = sorted([d.rstrip('/') for d in dirs if d.strip()])

        print(f"Found {len(clean_dirs)} top-level directories:")
        for i, dir_name in enumerate(clean_dirs, 1):
            print(f"{i:3d}. {dir_name}")

    except subprocess.CalledProcessError as e:
        print(f"Error listing directories on remote '{remote_name}': {e.stderr}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

def parse_arguments() -> ScriptArgs:
    """Parses command-line arguments and returns them as a ScriptArgs object."""
    parser = argparse.ArgumentParser(
        description="Copy a directory structure from an rclone source to a local directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("remote_name", nargs='?', default=None, help="Name of the rclone source remote (e.g., 'dropbox').")
    parser.add_argument("source_dir", nargs='?', default=None, help="The source directory to copy from (e.g., 'media/').")
    parser.add_argument(
        "-d", "--dest-dir",
        type=Path,
        default=Path.home() / "Downloads",
        help="The local directory to download files to. Defaults to the user's Downloads folder."
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="If set, flatten the directory structure, saving all files to the root of the destination directory."
    )
    parser.add_argument(
        "-s", "--separator",
        type=str,
        default="_",
        help="The character to use when flattening directory names into album names. Defaults to '_'."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only print the actions that would be taken without copying any files."
    )
    parser.add_argument(
        "--show-remotes",
        action="store_true",
        help="If set, display the configured rclone remotes and exit."
    )
    parser.add_argument(
        "-l", "--list-remote-top-dirs",
        action="store_true",
        help="If set, list top-level directories on the remote and exit."
    )
    parser.add_argument(
        "-f", "--file-types",
        nargs='*',
        choices=['images', 'videos', 'docs', 'audio'],
        help="Filter files by type. Options: images, videos, docs, audio. Can specify multiple types."
    )
    parser.add_argument(
        "--delete-after-download",
        action="store_true",
        help="Delete files from remote after successful download and validation."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode - prompt for confirmation at key decision points."
    )
    args = parser.parse_args()

    if args.show_remotes:
        show_remotes()

    if args.list_remote_top_dirs:
        if not args.remote_name:
            parser.error("remote_name is required when using --list-remote-top-dirs")
        list_remote_top_dirs(args.remote_name)

    if not args.show_remotes and not args.list_remote_top_dirs and not all([args.remote_name, args.source_dir]):
        parser.error("the following arguments are required: remote_name, source_dir")

    return ScriptArgs(
        remote_name=args.remote_name,
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        flatten=args.flatten,
        separator=args.separator,
        dry_run=args.dry_run,
        show_remotes=args.show_remotes,
        list_remote_top_dirs=args.list_remote_top_dirs,
        file_types=args.file_types,
        delete_after_download=args.delete_after_download,
        interactive=args.interactive
    )

def get_source_dirs(remote_name: str, source_dir: str) -> List[str]:
    """Uses `rclone lsf -R` to get a recursive list of all files and infers the directories."""
    command = ["rclone", "lsf", "-R", f"{remote_name}:{source_dir}"]
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        if not files or all(f == '' for f in files):
            return []

        dir_set: Set[str] = set()
        for file_path in files:
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                dir_set.add(parent_dir)

        sorted_dirs = sorted(list(dir_set))
        print(f"Found {len(sorted_dirs)} unique directories containing files.")
        return sorted_dirs
    except subprocess.CalledProcessError as e:
        print(f"Error listing files with rclone: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def flatten_path(path: str, separator: str) -> str:
    """Replaces directory separators and spaces with a custom separator."""
    path_no_slashes = path.replace('/', separator).replace('\\', separator)
    return path_no_slashes.replace(' ', separator)

def build_file_type_filters(file_types: Optional[List[str]]) -> List[str]:
    """Builds rclone include filters based on specified file types."""
    if not file_types:
        return []

    include_filters = []
    for file_type in file_types:
        if file_type in FILE_TYPE_MAPPINGS:
            extensions = FILE_TYPE_MAPPINGS[file_type]
            for ext in extensions:
                # Add both lowercase and uppercase versions
                include_filters.extend([f"--include=*{ext}", f"--include=*{ext.upper()}"])

    return include_filters

def collect_file_statistics(remote_name: str, source_dir: str, file_types: Optional[List[str]]) -> Dict:
    """Collects detailed file statistics from the remote."""
    stats = {
        'total_files': 0,
        'files_by_type': {'images': 0, 'videos': 0, 'docs': 0, 'audio': 0, 'other': 0},
        'total_size_bytes': 0,
        'files_included': 0,
        'files_excluded': 0,
        'max_depth': 0,
        'excluded_files': [],
        'included_files': []
    }
    
    try:
        # Get file list with sizes
        result = subprocess.run(
            ["rclone", "lsf", "-R", "--format", "pst", f"{remote_name}:{source_dir}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        if not files or all(f == '' for f in files):
            return stats
        
        # Build include patterns for filtering
        include_extensions = set()
        if file_types:
            for file_type in file_types:
                if file_type in FILE_TYPE_MAPPINGS:
                    include_extensions.update(ext.lower() for ext in FILE_TYPE_MAPPINGS[file_type])
        
        for file_line in files:
            if not file_line.strip():
                continue
                
            parts = file_line.split(';')
            if len(parts) < 3:
                continue
                
            file_path = parts[0]
            file_size = int(parts[1]) if parts[1].isdigit() else 0
            
            # Skip directories
            if file_path.endswith('/'):
                continue
                
            stats['total_files'] += 1
            stats['total_size_bytes'] += file_size
            
            # Calculate depth
            depth = file_path.count('/')
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            file_type_found = 'other'
            
            for type_name, extensions in FILE_TYPE_MAPPINGS.items():
                if file_ext in [ext.lower() for ext in extensions]:
                    file_type_found = type_name
                    break
            
            stats['files_by_type'][file_type_found] += 1
            
            # Check if file would be included by filter
            if not file_types or file_ext in include_extensions:
                stats['files_included'] += 1
                stats['included_files'].append({
                    'path': file_path,
                    'size': file_size,
                    'type': file_type_found
                })
            else:
                stats['files_excluded'] += 1
                stats['excluded_files'].append(file_path)
                
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not collect detailed statistics: {e.stderr}", file=sys.stderr)
        
    return stats

def display_statistics(stats: Dict, args: ScriptArgs, execution_time: float, is_dry_run: bool):
    """Displays comprehensive statistics about the operation."""
    print("\n" + "="*50)
    print("OPERATION STATISTICS")
    print("="*50)
    
    # File Statistics
    print("\n📁 File Statistics:")
    if is_dry_run:
        print(f"  • Total files found: {stats['total_files']}")
    else:
        print(f"  • Total files copied: {stats['total_files']}")
        
    if stats['files_by_type']:
        type_counts = []
        for file_type, count in stats['files_by_type'].items():
            if count > 0:
                type_counts.append(f"{file_type}: {count}")
        if type_counts:
            print(f"  • Files by type: {', '.join(type_counts)}")
    
    # Convert bytes to human readable format
    if stats['total_size_bytes'] > 0:
        size_mb = stats['total_size_bytes'] / (1024 * 1024)
        if size_mb >= 1024:
            size_gb = size_mb / 1024
            print(f"  • Total data size: {size_gb:.1f} GB")
        else:
            print(f"  • Total data size: {size_mb:.1f} MB")
    
    print(f"  • Number of directories processed: {len(stats.get('directories', []))}")
    
    # Performance Statistics
    print(f"\n⏱️  Performance Statistics:")
    print(f"  • Execution time: {execution_time:.2f} seconds")
    
    # Filter Statistics
    if args.file_types:
        print(f"\n🔍 Filter Statistics:")
        print(f"  • Files included by type filters: {stats['files_included']}")
        print(f"  • Files excluded by type filters: {stats['files_excluded']}")
        
        # Show excluded file paths (limit to first 20 for readability)
        if stats.get('excluded_files') and len(stats['excluded_files']) > 0:
            print(f"  • Excluded file paths:")
            excluded_files = stats['excluded_files']
            display_count = min(20, len(excluded_files))
            
            for i, file_path in enumerate(excluded_files[:display_count]):
                print(f"    - {file_path}")
            
            if len(excluded_files) > display_count:
                print(f"    ... and {len(excluded_files) - display_count} more files")
    
    # Operation Statistics (for actual runs)
    if not is_dry_run:
        print(f"\n✅ Operation Statistics:")
        print(f"  • Files successfully copied: {stats.get('files_copied', 'N/A')}")
        print(f"  • Files failed: {stats.get('files_failed', 0)}")
        print(f"  • Files skipped: {stats.get('files_skipped', 0)}")
        print(f"  • Directories created: {stats.get('directories_created', 'N/A')}")
        
        # Validation Statistics
        validation = stats.get('validation_results')
        if validation:
            print(f"\n🔍 Validation Results:")
            print(f"  • Files validated: {validation['files_validated']}")
            print(f"  • Files missing: {validation['files_missing']}")
            print(f"  • Files with size mismatch: {validation['files_size_mismatch']}")
            
            # Show missing files (limit to first 10)
            if validation['missing_files']:
                print(f"  • Missing files:")
                for i, missing in enumerate(validation['missing_files'][:10]):
                    print(f"    - {missing['remote_path']}")
                if len(validation['missing_files']) > 10:
                    print(f"    ... and {len(validation['missing_files']) - 10} more missing files")
            
            # Show size mismatch files (limit to first 5)
            if validation['size_mismatch_files']:
                print(f"  • Size mismatch files:")
                for i, mismatch in enumerate(validation['size_mismatch_files'][:5]):
                    print(f"    - {mismatch['remote_path']} (expected: {mismatch['expected_size']} bytes, actual: {mismatch['actual_size']} bytes)")
                if len(validation['size_mismatch_files']) > 5:
                    print(f"    ... and {len(validation['size_mismatch_files']) - 5} more size mismatches")
        
        # Deletion Statistics
        deletion = stats.get('deletion_results')
        if deletion:
            print(f"\n🗑️  Deletion Results:")
            print(f"  • Files deleted from remote: {deletion['files_deleted']}")
            print(f"  • Files failed to delete: {deletion['files_failed_to_delete']}")
            
            # Show failed deletions (limit to first 5)
            if deletion['failed_deletions']:
                print(f"  • Failed deletions:")
                for i, failed in enumerate(deletion['failed_deletions'][:5]):
                    print(f"    - {failed['path']}: {failed['error']}")
                if len(deletion['failed_deletions']) > 5:
                    print(f"    ... and {len(deletion['failed_deletions']) - 5} more failed deletions")
    
    # Flattened Operations
    if args.flatten:
        print(f"\n🔄 Flattened Operations:")
        print(f"  • Original directory structure depth: {stats.get('max_depth', 0)} levels")
        print(f"  • Directory name transformations applied: {stats.get('transformations_applied', len(stats.get('directories', [])))}")
    
    print("="*50)

def validate_downloaded_files(args: ScriptArgs, included_files: List[Dict]) -> Dict:
    """Validates that all expected files were actually downloaded."""
    validation_results = {
        'files_validated': 0,
        'files_missing': 0,
        'files_size_mismatch': 0,
        'missing_files': [],
        'size_mismatch_files': [],
        'successfully_validated_files': []
    }
    
    print("\nValidating downloaded files...")
    
    for file_info in included_files:
        remote_path = file_info['path']
        expected_size = file_info['size']
        
        # Determine local path based on flattening
        if args.flatten:
            # For flattened structure, file goes into flattened directory
            dir_path = os.path.dirname(remote_path)
            file_name = os.path.basename(remote_path)
            if dir_path:
                flattened_dir = flatten_path(dir_path, args.separator)
                local_path = args.dest_dir / flattened_dir / file_name
            else:
                local_path = args.dest_dir / file_name
        else:
            # For preserved structure, maintain original path
            local_path = args.dest_dir / remote_path
        
        validation_results['files_validated'] += 1
        
        # Check if file exists
        if not local_path.exists():
            validation_results['files_missing'] += 1
            validation_results['missing_files'].append({
                'remote_path': remote_path,
                'expected_local_path': str(local_path)
            })
            continue
        
        # Check file size
        try:
            local_size = local_path.stat().st_size
            if local_size != expected_size:
                validation_results['files_size_mismatch'] += 1
                validation_results['size_mismatch_files'].append({
                    'remote_path': remote_path,
                    'local_path': str(local_path),
                    'expected_size': expected_size,
                    'actual_size': local_size
                })
            else:
                # File exists and size matches - successfully validated
                validation_results['successfully_validated_files'].append(file_info)
        except OSError as e:
            print(f"Warning: Could not check size for {local_path}: {e}", file=sys.stderr)
    
    return validation_results

def perform_post_operation_validation(args: ScriptArgs, stats: Dict) -> None:
    """Performs post-operation validation and updates statistics."""
    if not stats.get('included_files'):
        return
    
    validation_results = validate_downloaded_files(args, stats['included_files'])
    stats['validation_results'] = validation_results
    
    # Print validation summary
    total_expected = validation_results['files_validated']
    missing = validation_results['files_missing']
    size_mismatch = validation_results['files_size_mismatch']
    successful = total_expected - missing - size_mismatch
    
    print(f"\nValidation Summary: {successful}/{total_expected} files validated successfully")
    if missing > 0:
        print(f"⚠️  Warning: {missing} files are missing from local destination")
    if size_mismatch > 0:
        print(f"⚠️  Warning: {size_mismatch} files have size mismatches")
    
    # Delete validated files from remote if requested
    if args.delete_after_download and validation_results['successfully_validated_files']:
        files_to_delete = len(validation_results['successfully_validated_files'])
        
        # Interactive confirmation before deletion
        if args.interactive:
            print(f"\n⚠️  About to delete {files_to_delete} validated files from remote '{args.remote_name}'")
            if not prompt_user_confirmation("Are you sure you want to delete these files from the remote?", "n"):
                print("Deletion cancelled by user. Files remain on remote.")
                return
        
        deletion_results = delete_validated_files_from_remote(
            args, 
            validation_results['successfully_validated_files']
        )
        stats['deletion_results'] = deletion_results

def delete_validated_files_from_remote(args: ScriptArgs, validated_files: List[Dict]) -> Dict:
    """Deletes successfully validated files from the remote."""
    deletion_results = {
        'files_to_delete': len(validated_files),
        'files_deleted': 0,
        'files_failed_to_delete': 0,
        'failed_deletions': []
    }
    
    if not validated_files:
        return deletion_results
    
    print(f"\nDeleting {len(validated_files)} validated files from remote...")
    
    for file_info in validated_files:
        remote_file_path = f"{args.remote_name}:{args.source_dir}/{file_info['path']}"
        
        try:
            result = subprocess.run(
                ["rclone", "delete", remote_file_path],
                capture_output=True,
                text=True,
                check=True
            )
            deletion_results['files_deleted'] += 1
            print(f"Deleted: {file_info['path']}")
            
        except subprocess.CalledProcessError as e:
            deletion_results['files_failed_to_delete'] += 1
            deletion_results['failed_deletions'].append({
                'path': file_info['path'],
                'error': e.stderr.strip()
            })
            print(f"Failed to delete {file_info['path']}: {e.stderr.strip()}", file=sys.stderr)
    
    # Print deletion summary
    deleted = deletion_results['files_deleted']
    failed = deletion_results['files_failed_to_delete']
    total = deletion_results['files_to_delete']
    
    print(f"\nDeletion Summary: {deleted}/{total} files deleted from remote")
    if failed > 0:
        print(f"⚠️  Warning: {failed} files could not be deleted from remote")
    
    return deletion_results

def display_program_arguments(args: ScriptArgs) -> None:
    """Displays the program arguments in a clear format."""
    print("\n" + "="*50)
    print("PROGRAM CONFIGURATION")
    print("="*50)
    print(f"Remote name: {args.remote_name}")
    print(f"Source directory: {args.source_dir}")
    print(f"Destination directory: {args.dest_dir}")
    print(f"Flatten directories: {'Yes' if args.flatten else 'No'}")
    if args.flatten:
        print(f"Directory separator: '{args.separator}'")
    print(f"File types filter: {', '.join(args.file_types) if args.file_types else 'All files'}")
    print(f"Dry run mode: {'Yes' if args.dry_run else 'No'}")
    print(f"Delete after download: {'Yes' if args.delete_after_download else 'No'}")
    print(f"Interactive mode: {'Yes' if args.interactive else 'No'}")
    print("="*50)

def generate_copy_plan(args: ScriptArgs, source_dirs: List[str]):
    """Generates and prints the detailed plan of copy operations."""
    print("\n--- Copy Plan ---")
    if args.file_types:
        print(f"File types filter: {', '.join(args.file_types)}")
    for src_dir in source_dirs:
        source_path = f"{args.remote_name}:{args.source_dir}/{src_dir}"
        if args.flatten:
            flattened_name = flatten_path(src_dir, args.separator)
            dest_path = args.dest_dir / flattened_name
            print(f"Source: '{source_path}' ==> Destination: '{dest_path}'")
        else:
            dest_path = args.dest_dir / src_dir
            print(f"Source: '{source_path}' ==> Destination: '{dest_path}'")

def execute_dry_run():
    """Prints a message for the user indicating a dry run is complete."""
    print("\n--- Dry Run Complete ---")
    print("The above copy operations would be performed. No files will be copied.")

def execute_copy(args: ScriptArgs, source_dirs: List[str]):
    """Executes the rclone copy command."""
    print("\n--- Starting Copy Process ---")

    # Build file type filters
    file_filters = build_file_type_filters(args.file_types)

    if args.flatten:
        for src_dir in source_dirs:
            source_path = f"{args.remote_name}:{args.source_dir}/{src_dir}"
            flattened_name = flatten_path(src_dir, args.separator)
            dest_path = str(args.dest_dir / flattened_name)
            print(f"\nCopying from '{source_path}' to '{dest_path}' (flattened)... ")
            command = ["rclone", "copy", source_path, dest_path, "--progress"] + file_filters
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during copy: {e}", file=sys.stderr)
    else:
        source_path = f"{args.remote_name}:{args.source_dir}"
        dest_path = str(args.dest_dir)
        print(f"\nCopying from '{source_path}' to '{dest_path}' (preserving structure)... ")
        command = ["rclone", "copy", source_path, dest_path, "--progress"] + file_filters
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during copy: {e}", file=sys.stderr)

    print("\n--- All tasks complete. ---")

def main():
    """Main function to orchestrate the script's operations."""
    start_time = time.time()
    
    print("--- Starting Remote Downloader Script ---")

    check_rclone_exists()
    args = parse_arguments()

    # Early exit functions already handle their own logic
    if args.show_remotes or args.list_remote_top_dirs:
        return

    # Display program configuration and prompt for confirmation in interactive mode
    display_program_arguments(args)
    
    if args.interactive:
        if not prompt_user_confirmation("Do you want to proceed with these settings?"):
            print("Operation cancelled by user.")
            return

    # Collect file statistics
    print("Collecting file statistics...")
    stats = collect_file_statistics(args.remote_name, args.source_dir, args.file_types)
    stats['directories'] = get_source_dirs(args.remote_name, args.source_dir)
    
    if not stats['directories']:
        print("No source directories found to process.")
        return

    generate_copy_plan(args, stats['directories'])

    if args.dry_run:
        execute_dry_run()
    else:
        execute_copy(args, stats['directories'])
        perform_post_operation_validation(args, stats)
    
    # Display statistics
    execution_time = time.time() - start_time
    display_statistics(stats, args, execution_time, args.dry_run)

if __name__ == "__main__":
    main()