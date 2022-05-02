import os, sys
import subprocess
import shutil

def extract(dir_path):
    files = os.listdir(dir_path)
    owd = os.getcwd()
    os.chdir(dir_path)
    for file in files:
        if file.endswith(".tar.gz"):
            p=subprocess.Popen(['tar', '-xvf', file])
    os.chdir(owd)

def copy2(nb_path):
    with open(os.path.join(nb_path, "nbs.txt")) as f:
        nbs = f.read().splitlines()
    for i, nb in enumerate(nbs):
        shutil.copy2(nb, os.path.join(nb_path, f"nb_{i}.ipynb"))

def nb_convert(dir_path):
    files = os.listdir(dir_path)
    owd = os.getcwd()
    os.chdir(dir_path)
    for file in files:
        if file.endswith(".ipynb"):
            p=subprocess.Popen(['jupyter', 'nbconvert', file, '--to', 'python'])
    os.chdir(owd)

def process(date):
    repo_path = os.path.join("GitHub-data", "github-repos", date)
    extract(repo_path)
    nb_path = os.path.join("GitHub-data", "notebooks", date)
    repo_path = nb_path = "kaggle-notebooks/house-prices-advanced-regression-techniques_voted"
    if not os.path.exists(nb_path):
        os.mkdir(nb_path)      
    os.system(f"grep -e torch -e keras -e sklearn -rl --include='*.ipynb' --exclude-dir='.*' {repo_path}/* | sort > {os.path.join(nb_path, 'nbs.txt')}")
    copy2(nb_path)
    nb_convert(nb_path)

if __name__ == "__main__":
    # process("date")
    dates = ["2021-09-" + str(date).zfill(2) for date in range(1, 31)]
    # dates = ["2021-01-05"]
    for date in dates:
        process(date)