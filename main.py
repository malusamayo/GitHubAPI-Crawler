import os, sys
import subprocess
import json
import argparse
from datetime import datetime, timedelta
from github_api import GitHubAPI, _tokens
from tqdm import tqdm

MAX_SIZE_MB = 100  # for example, skip repos >100 MB

def generate_date_range(start_date, end_date):
    """
    Generate a list of dates from start_date to end_date (inclusive).

    Args:
        start_date: Start date in format "YYYY-MM-DD"
        end_date: End date in format "YYYY-MM-DD"

    Returns:
        List of date strings in format "YYYY-MM-DD"
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

def download(repo, date, dir_path="github-repos"):
    repo_size_mb = repo.get('size', 0) / 1024  # convert from KB to MB
    # print(repo_size_mb)
    if repo_size_mb > MAX_SIZE_MB:
        print(f"Skipping {repo['full_name']} ({repo_size_mb:.1f} MB)")
        return

    download_path = repo['url'] + '/tarball'
    dir_path = os.path.join(dir_path, date)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    output_path = os.path.join(dir_path, repo['full_name'].replace('/', '-') + ".tar.gz")

    if os.path.exists(output_path):
        # print("Already downloaded!")
        return

    subprocess.Popen([
        'curl', '-H', f'Authorization: token {_tokens[0]}',
        '-L', download_path, '-o', output_path
    ])

def write_metadata(data, date, dir_path="github-repos"):
    output_path = os.path.join(dir_path, date, "metadata.txt")
    with open(output_path, 'w') as f:
        f.write(json.dumps(data))

def main():
    parser = argparse.ArgumentParser(
        description="Download GitHub repositories for specified date range"
    )
    parser.add_argument(
        '--start-date',
        required=True,
        help='Start date in format YYYY-MM-DD (e.g., 2025-01-01)'
    )
    parser.add_argument(
        '--end-date',
        required=True,
        help='End date in format YYYY-MM-DD (e.g., 2025-02-28)'
    )
    parser.add_argument(
        '--language',
        default='Python',
        help='Programming language to search for (default: Python)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=12,
        help='Time interval in hours for API queries (default: 12)'
    )
    parser.add_argument(
        '--output-dir',
        default='github-repos',
        help='Output directory for downloaded repositories (default: github-repos)'
    )
    parser.add_argument(
        '--max-size',
        type=int,
        default=100,
        help='Maximum repository size in MB to download (default: 100)'
    )

    args = parser.parse_args()

    # Update global MAX_SIZE_MB
    global MAX_SIZE_MB
    MAX_SIZE_MB = args.max_size

    api = GitHubAPI()

    # Generate date range
    dates = generate_date_range(args.start_date, args.end_date)

    # Generate time pairs based on interval
    time_pairs = [
        (f"T{str(x).zfill(2)}:00:00", f"T{str(x+args.interval-1).zfill(2)}:59:59")
        for x in range(0, 24, args.interval)
    ]

    # Process each date
    for date in tqdm(dates, desc="Processing dates"):
        meta_data = []
        for st, ed in tqdm(time_pairs, desc=f"Time intervals for {date}", leave=False):
            res = api.get_repo(args.language, date+st, date+ed)
            for repo in tqdm(res['items'], desc="Downloading repos", leave=False):
                download(repo, date, dir_path=args.output_dir)
            meta_data += res['items']
        write_metadata(meta_data, date, dir_path=args.output_dir)


if __name__ == "__main__":
    main()

# compare download cnts:
# startdate='2021-09-01'; echo {0..6} | xargs -I{} -d ' ' date --date="$startdate +"{}" days" +"%Y-%m-%d" |  while read DATE ; do (echo $DATE; ls github-repos/$DATE -l | wc -l; curl -s https://api.github.com/search/repositories\?q\=language%3A%22Jupyter%20Notebook%22+created%3A$DATE\&s\=stars | jq .total_count;) done