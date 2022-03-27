import os, sys
import subprocess
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
        subprocess.Popen(['curl', '-H', 'Authorization: token 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', '-L', download_path, '-o', output_path])

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
    dates = ["2021-09-" + str(date).zfill(2) for date in range(8, 15)]
    time_pairs = [("T00:00:00", "T03:59:59"), ("T04:00:00", "T07:59:59"), ("T08:00:00", "T11:59:59"), ("T12:00:00", "T15:59:59"), ("T16:00:00", "T19:59:59"), ("T20:00:00", "T23:59:59")]
    for date in dates:
        for st, ed in time_pairs:
            res = api.get_repo("Jupyter%20Notebook",date+st,date+ed)
            for repo in res['items']:
                download(repo, date)

# compare download cnts:
# startdate='2021-09-01'; echo {0..6} | xargs -I{} -d ' ' date --date="$startdate +"{}" days" +"%Y-%m-%d" |  while read DATE ; do (echo $DATE; ls github-repos/$DATE -l | wc -l; curl -s https://api.github.com/search/repositories\?q\=language%3A%22Jupyter%20Notebook%22+created%3A$DATE\&s\=stars | jq .total_count;) done