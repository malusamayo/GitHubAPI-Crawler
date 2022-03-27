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

if __name__ == "__main__":
    date = "2021-01-06"
    # extract(os.path.join("github-repos", date))
    nb_path = os.path.join("notebooks", date)
    if not os.path.exists(nb_path):
        os.mkdir(nb_path)      
    os.system(f"grep -e torch -e keras -e sklearn -rl --include='*.ipynb' --exclude-dir='.*' github-repos/{date}/* | sort > {os.path.join(nb_path, 'nbs.txt')}")
    copy2(nb_path)
    nb_convert(nb_path)