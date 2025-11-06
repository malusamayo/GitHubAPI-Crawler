import os, sys
import subprocess
import json
from github_api import GitHubAPI

def download(repo, date):
    download_path = repo['url'] + '/tarball'
    dir_path = os.path.join("github-repos", date)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    output_path = os.path.join("github-repos", date, repo['full_name'].replace('/', '-') + ".tar.gz")
    if os.path.exists(output_path):
        pass
        # print("Already downloaded!")
    else:
        subprocess.Popen(['curl', '-H', 'Authorization: token INSERT_TOKEN_HERE', '-L', download_path, '-o', output_path])

def write_metadata(data, date):
    output_path = os.path.join("GitHub-data", "github-repos", date, "metadata.txt")
    with open(output_path, 'w') as f:
        f.write(json.dumps(data))

if __name__ == "__main__":
    api = GitHubAPI()
    # # query github api with URL https://api.github.com/repos/jquery/jquery/pulls/4406/commits
    #     # res = api.request("repos/jquery/jquery/pulls/4406/commits")
    #     #

    # query issue/pr timeline
    #  api doc: https://developer.github.com/v3/issues/timeline/#list-timeline-events-for-an-issue
    # the following query the events for https://github.com/jquery/jquery/pull/4406/
    # events = api.get_issue_pr_timeline("jquery/jquery", 4406)


    #Search repos
    dates = ["2025-09-" + str(date).zfill(2) for date in range(30, 31)]
    # dates = ["2021-09-06"]
    interval = 1
    time_pairs = [(f"T{str(x).zfill(2)}:00:00", f"T{str(x+interval-1).zfill(2)}:59:59") for x in range(0, 24, interval)]
    for date in dates:
        meta_data = []
        for st, ed in time_pairs:
            res = api.get_repo("Python",date+st,date+ed)
            for repo in res['items']:
                download(repo, date)
            meta_data += res['items']
        write_metadata(meta_data, date)

# compare download cnts:
# startdate='2021-09-01'; echo {0..6} | xargs -I{} -d ' ' date --date="$startdate +"{}" days" +"%Y-%m-%d" |  while read DATE ; do (echo $DATE; ls github-repos/$DATE -l | wc -l; curl -s https://api.github.com/search/repositories\?q\=language%3A%22Jupyter%20Notebook%22+created%3A$DATE\&s\=stars | jq .total_count;) done