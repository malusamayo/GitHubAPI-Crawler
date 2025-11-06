import os
import sys
import subprocess
import argparse
from multiprocessing import Pool, cpu_count
from pathlib import Path


def extract(dir_path):
    """
    Extract all .tar.gz files in the directory using tar command.

    Args:
        dir_path: Directory containing .tar.gz files
    """
    files = os.listdir(dir_path)
    owd = os.getcwd()
    os.chdir(dir_path)
    for file in files:
        if file.endswith(".tar.gz"):
            p=subprocess.Popen(['tar', '-xvf', file])
    os.chdir(owd)


def search_keyword_in_repo(args):
    """
    Search for one or more keywords in all files of a repository.

    Args:
        args: Tuple of (repo_path, keywords, output_dir, file_extensions)

    Returns:
        Tuple of (repo_name, found, matching_files_count, matching_files)
    """
    repo_path, keywords, output_dir, file_extensions = args
    repo_name = os.path.basename(repo_path)

    if not os.path.exists(repo_path):
        return (repo_name, False, 0, [])

    # Build the grep command using shell to allow glob expansion
    cmd = f"grep -rl -F"

    # Add case-insensitive flag if needed
    # cmd += " -i"  # Uncomment for case-insensitive search

    # Add file extensions filter
    if file_extensions:
        for ext in file_extensions:
            # Remove leading dot if present
            ext = ext.lstrip('.')
            cmd += f" --include='*.{ext}'"

    # Exclude hidden directories
    cmd += " --exclude-dir='.*'"

    # Add multiple keywords (OR logic - match any keyword)
    for keyword in keywords:
        cmd += f" -e '{keyword}'"

    # Add the path with glob pattern
    cmd += f" {repo_path}/*"

    try:
        # Run grep command with shell=True to handle glob expansion
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Timeout after 30 seconds
        )

        matching_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        found = len(matching_files) > 0 and matching_files[0] != ''

        # Save results if keyword found
        if found and output_dir:
            output_file = os.path.join(output_dir, f"{repo_name}_matches.txt")
            with open(output_file, 'w') as f:
                f.write(f"Repository: {repo_path}\n")
                f.write(f"Keywords: {', '.join(keywords)}\n")
                f.write(f"Matching files:\n")
                for file in matching_files:
                    f.write(f"{file}\n")

        return (repo_name, found, len(matching_files) if found else 0, matching_files if found else [])

    except subprocess.TimeoutExpired:
        print(f"Warning: Search timeout for {repo_name}")
        return (repo_name, False, 0, [])
    except Exception as e:
        print(f"Error searching {repo_name}: {e}")
        return (repo_name, False, 0, [])


def process_repos(repos_dir, keywords, output_dir=None, file_extensions=None, num_workers=None, skip_extract=False):
    """
    Search for one or more keywords/phrases in multiple repositories in parallel.

    Args:
        repos_dir: Directory containing repositories or .tar.gz files
        keywords: List of keywords or phrases to search for (e.g., ["import torch", "import keras"])
        output_dir: Directory to save results (optional)
        file_extensions: List of file extensions to search (e.g., ['py', 'js'])
        num_workers: Number of parallel workers (defaults to CPU count)
        skip_extract: Skip extraction if repos are already extracted
    """
    # Get list of repositories
    if not os.path.exists(repos_dir):
        print(f"Error: Directory {repos_dir} does not exist")
        return

    # Check if we need to extract .tar.gz files
    if not skip_extract:
        extract(repos_dir)

    # Get list of extracted/existing repositories
    repo_paths = [
        os.path.join(repos_dir, d)
        for d in os.listdir(repos_dir)
        if os.path.isdir(os.path.join(repos_dir, d))
    ]

    if not repo_paths:
        print(f"No repositories found in {repos_dir}")
        return

    # Create output directory if needed
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare arguments for parallel processing
    args_list = [
        (repo_path, keywords, output_dir, file_extensions)
        for repo_path in repo_paths
    ]

    # Determine number of workers
    if num_workers is None:
        num_workers = min(cpu_count(), len(repo_paths))

    keywords_str = ', '.join([f"'{k}'" for k in keywords])
    print(f"Searching for {keywords_str} in {len(repo_paths)} repositories using {num_workers} workers...")

    # Process in parallel
    results = []
    with Pool(processes=num_workers) as pool:
        results = pool.map(search_keyword_in_repo, args_list)

    # Summarize results
    repos_with_keyword = [(name, count, files) for name, found, count, files in results if found]

    print("\n" + "="*60)
    print(f"Search complete!")
    print(f"Total repositories searched: {len(results)}")
    print(f"Repositories containing keywords: {len(repos_with_keyword)}")
    print("="*60)

    if repos_with_keyword:
        print("\nRepositories with matches:")
        for repo_name, count, files in sorted(repos_with_keyword, key=lambda x: x[1], reverse=True):
            print(f"  {repo_name}: {count} file(s)")
            for file_path in files[:5]:  # Show first 5 files
                print(f"    - {os.path.basename(file_path)}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

        # Save summary
        if output_dir:
            summary_file = os.path.join(output_dir, "summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"Keywords: {', '.join(keywords)}\n")
                if file_extensions:
                    f.write(f"File extensions: {', '.join(file_extensions)}\n")
                f.write(f"Total repositories searched: {len(results)}\n")
                f.write(f"Repositories with matches: {len(repos_with_keyword)}\n\n")
                f.write("Repositories with matches:\n")
                for repo_name, count, files in sorted(repos_with_keyword, key=lambda x: x[1], reverse=True):
                    f.write(f"  {repo_name}: {count} file(s)\n")
                    for file_path in files:
                        f.write(f"    - {file_path}\n")
            print(f"\nSummary saved to: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Search for a keyword in multiple repositories in parallel"
    )
    parser.add_argument(
        'repos_dir',
        help='Directory containing repositories to search'
    )
    parser.add_argument(
        'keywords',
        help='Keywords or phrases to search for (comma-separated, e.g., "import torch,import keras")',
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory for results (optional)',
        default=None
    )
    parser.add_argument(
        '-e', '--extensions',
        help='File extensions to search (comma-separated, e.g., py,js,txt)',
        default=None
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of parallel workers (default: CPU count)',
        default=None
    )
    parser.add_argument(
        '-i', '--case-insensitive',
        action='store_true',
        help='Perform case-insensitive search'
    )
    parser.add_argument(
        '--skip-extract',
        action='store_true',
        help='Skip extraction of .tar.gz files (use if repos already extracted)'
    )

    args = parser.parse_args()

    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(',')]

    # Parse file extensions
    file_extensions = None
    if args.extensions:
        file_extensions = [ext.strip() for ext in args.extensions.split(',')]

    # Run the search
    process_repos(
        args.repos_dir,
        keywords,
        args.output,
        file_extensions,
        args.workers,
        args.skip_extract
    )


if __name__ == "__main__":
    main()
