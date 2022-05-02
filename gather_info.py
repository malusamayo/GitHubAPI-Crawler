### Classify notebooks to three categories: tutorial vs assignment vs research 
### Classify notebooks based on stars
import os, sys, json
import re
import pandas as pd
import numpy as np

def gather_notebooks(nb_path, kws, output_file):
    os.system(f"grep -irl {' '.join(['-e '+kw for kw in kws])} --exclude='*.ir.py' {nb_path}/**/*.py | sort -V > {os.path.join(nb_path, output_file)}")

def gather_tutorials(nb_path):
    kws = ["this tutorial"]
    gather_notebooks(nb_path, kws, "tutorial.txt")

def gather_assignments(nb_path):
    kws = ["homework", "assignment"]
    gather_notebooks(nb_path, kws, "assignment.txt")

def gather_competitions(nb_path):
    kws = ["kaggle", "competition"]
    gather_notebooks(nb_path, kws, "competition.txt")
    

def get_notebooks(dir_path):
    files = os.listdir(dir_path)
    files = [f for f in files if f.endswith(".py") and not f.endswith(".ir.py")]
    nbs_path_file = os.path.join(dir_path, "nbs.txt")
    with open(nbs_path_file) as f:
        nbs = f.read().splitlines()
    repos = ['/'.join(nb.split('/')[3:4])[:-8] for nb in nbs]
    # print(repos)
    return repos

def get_metadata(dir_path):
    path = os.path.join(dir_path, "metadata.txt")
    with open(path) as f:
        data = json.loads(f.read())
    repo2stars = {repo['full_name'].replace('/', '-'): repo["stargazers_count"] for repo in data}
    return repo2stars
    
def build_nb_star_map(dir_path):
    dates = ["2021-09-" + str(date).zfill(2) for date in range(1, 31)]
    nb2stars = {}
    for date in dates:
        nb_path = os.path.join(dir_path, "notebooks", date)
        repo_path = os.path.join(dir_path, "github-repos", date)
        repos = get_notebooks(nb_path)
        repo2stars = get_metadata(repo_path)
        for i, repo in enumerate(repos):
            if repo in repo2stars:
                nb2stars[os.path.join(nb_path, f"nb_{i}.ipynb")] = repo2stars[repo]
    with open(os.path.join(dir_path, "nbstar.txt"), "w") as f:
        f.writelines([nb + "\t" + str(stars) + "\n" for nb, stars in nb2stars.items()])
# build_nb_star_map("GitHub-data")

def gather_top_nbs():
    df = pd.read_csv("GitHub-data/nbstar.txt", sep="\t", names=["repo", "stars"])
    # df2 = df.sort_values(by=['stars'], ascending=False)
    df2 = df[df["stars"]>=10]
    df2["repo"] = df2["repo"].str.replace(".ipynb", ".py")
    with open("GitHub-data/topnbs.txt", "w") as f:
        f.write("\n".join(list(df2["repo"])))

def gather_star_info():
    df = pd.read_csv("GitHub-data/nbstar.txt", sep="\t", names=["repo", "stars"])
    print(df["stars"].quantile(0.9), df[df["stars"]>=10]["stars"].quantile(0.9))
    with open("GitHub-data/assignment.txt") as f:
        lines = f.read().splitlines()
        lines = [l.replace(".py", ".ipynb") for l in lines]
    print(df.loc[df["repo"].isin(lines)]["stars"].quantile(0.9))
    with open("GitHub-data/tutorial.txt") as f:
        lines = f.read().splitlines()
        lines = [l.replace(".py", ".ipynb") for l in lines]
    print(df.loc[df["repo"].isin(lines)]["stars"].quantile(0.9))

def count_lines(nb_path):
    try:
        nb = json.load(open(nb_path))
    except Exception:
        return None
    if 'cells' in nb.keys():
        cells = nb['cells']
        return sum(len(c['source']) for c in cells if c['cell_type'] == 'code')
    else:
        return None

def count_lines_multiple(files):
    all_loc = []
    for f in files:
        print(f)
        loc = count_lines(f)
        if loc != None:
            all_loc.append(loc)
    print(np.mean(all_loc))

def gather_acc_sammple():
    df = pd.read_csv("GitHub-data/nbstar.txt", sep="\t", names=["repo", "stars"])
    df2 = df.sample(100)
    df2["repo"] = df2["repo"].str.replace(".ipynb", ".py")
    with open("GitHub-data/sample.txt", "w") as f:
        f.write("\n".join(list(df2["repo"])))

def calculate_time(file_path):
    df = pd.read_csv(file_path, sep="\t", index_col=False, names=["nb", "msg", "t1", "t2", "t3", "t"])
    df2 = df[df["msg"] == "Success!"]
    df2["p1"] = df2["t1"] / df2["t"]
    df2["p2"] = df2["t2"] / df2["t"]
    df2["p3"] = df2["t3"] / df2["t"]
    for col in df2.select_dtypes(include=np.number).columns:
        print(col, "{:.2f}\t{:.2f}\t{:.2f}".format(df2[col].max(), df2[col].mean(), df2[col].median()))
    return df2

def calculate_time_multiple(files):
    df2 = pd.DataFrame()
    for file in files:
        df = calculate_time(file)
        df2 = pd.concat(df2, df)
    for col in df2.select_dtypes(include=np.number).columns:
        print(col, "{:.2f}\t{:.2f}\t{:.2f}".format(df2[col].max(), df2[col].mean(), df2[col].median()))


def collect_success_nbs():
    # analyze whole log
    dates = ["2021-09-" + str(date).zfill(2) for date in range(1, 31)]
    df = pd.DataFrame()
    for date in dates:
        file_path = f"/usr0/home/cyang3/Projects/GitHubAPI-Crawler/GitHub-data/notebooks/{date}/log.txt"
        df_temp = pd.read_csv(file_path, sep="\t", index_col=False, names=["nb", "msg", "t1", "t2", "t3", "t"])
        df_temp["nb"] = df_temp["nb"].map(lambda x: os.path.join(date, x))
        df = pd.concat([df, df_temp])
    df = df[df["msg"] != "Conversion failed"]
    df["nb"] = df["nb"].map(lambda x: os.path.join("GitHub-data", "notebooks", x))
    return df

def find_results(file_path):
    file_path = file_path.replace(".py", "-fact")
    train_model = os.path.join(file_path, "TrainingDataWithModel.csv")
    val_model = os.path.join(file_path, "ValDataWithModel.csv")
    test_model = os.path.join(file_path, "TestDataWithModel.csv")
    model_pairs = os.path.join(file_path, "ModelPair.csv")
    pre_leaks = os.path.join(file_path, "Telemetry_FinalPreProcessingLeak.csv")
    overlap_leaks = os.path.join(file_path, "FinalOverlapLeak.csv")
    multi_leaks = os.path.join(file_path, "FinalNoTestDataWithMultiUse.csv")
    has_train = len(open(train_model).read().splitlines())
    has_val = len(open(val_model).read().splitlines())
    has_test = len(open(test_model).read().splitlines())
    has_pairs = len(open(model_pairs).read().splitlines())
    has_pre_leaks = len(open(pre_leaks).read().splitlines())
    has_overlap_leaks = len(open(overlap_leaks).read().splitlines())
    has_multi_leaks = len(open(multi_leaks).read().splitlines()) > 0
    return {"train":has_train, "val":has_val, "test":has_test, "model": has_pairs, "pre": has_pre_leaks, "overlap": has_overlap_leaks, "multi": has_multi_leaks}
    
def collect_leakmeth(file_path):
    file_path = file_path.replace(".py", "-fact")
    pre_leaks = os.path.join(file_path, "Telemetry_FinalPreProcessingLeak.csv")
    call = os.path.join(file_path, "CallGraphEdge.csv")
    taints = os.path.join(file_path, "TaintStartsTarget.csv")
    pre = pd.read_csv(pre_leaks, sep="\t", names=['trainModel', 'train', 'trainInvo', 'trainMeth', 'ctx1', 'testModel', 'test', 'testInvo', 'testMeth', 'ctx2', 'des', 'src'])
    leaksrc = pd.read_csv(taints, sep="\t", names=['to', 'toCtx', 'from', 'fromCtx', 'invo', 'meth', 'label'])
    meths = pd.read_csv(call, sep="\t", names=['invo', 'ctx', 'meth', 'ctx2'])
    merged =  pd.merge(pre, leaksrc, left_on="src", right_on="from")
    return {"leak_meth": list(merged["meth"]), 'meth': list(meths['meth'])}

def collect_leaks():
    df = collect_success_nbs()
    df = df[["nb", "msg"]]
    df = df[df["msg"] == "Success!"]
    # df['leak_meth'] = df.apply(lambda row: collect_leakmeth(row["nb"]), axis='columns')
    applied_df = df.apply(lambda row: collect_leakmeth(row["nb"]), axis='columns', result_type='expand')
    df = pd.concat([df, applied_df], axis='columns')
    def translate(x):
        try:
            meth = x.split(".")[-1]
            if meth not in ["fit", "fit_transform"]:
                return meth
            return x
        except:
            return x
    df['leak_meth'] = df['leak_meth'].map(lambda ms: [translate(m) for m in ms])
    df['meth'] = df['meth'].map(lambda ms: [translate(m) for m in ms])
    df['has_PCA'] = df['meth'].map(lambda ms: any(m in ms for m in ['PCA.fit_transform', 'PCA.fit']))
    df['has_mean'] = df['meth'].map(lambda ms: any(m in ms for m in ['mean', 'std']))
    df['has_scaler'] = df['meth'].map(lambda ms: any(m in ms for m in ['MinMaxScaler.fit_transform', 'StandardScaler.fit_transform', 'RobustScaler.fit_transform', 'MaxAbsScaler.fit_transform', 'MinMaxScaler.fit', 'StandardScaler.fit', 'RobustScaler.fit', 'MaxAbsScaler.fit']))
    df['leak_PCA'] = df['leak_meth'].map(lambda ms: any(m in ms for m in ['PCA.fit_transform', 'PCA.fit']))
    df['leak_mean'] = df['leak_meth'].map(lambda ms: any(m in ms for m in ['mean', 'std']))
    df['leak_scaler'] = df['leak_meth'].map(lambda ms: any(m in ms for m in ['MinMaxScaler.fit_transform', 'StandardScaler.fit_transform', 'RobustScaler.fit_transform', 'MaxAbsScaler.fit_transform', 'MinMaxScaler.fit', 'StandardScaler.fit', 'RobustScaler.fit', 'MaxAbsScaler.fit']))
    df.drop(['leak_meth', 'meth'], axis=1, inplace=True)
    return df





df = collect_leaks()

# count = df.groupby(df).count().sort_values(ascending=False)
# count = count.reset_index()
# count = count.rename(columns={"index": "meth", 0: "cnt"})
print(df)
df.to_csv("leak_meth_data.csv")

# calculate_time("/usr0/home/cyang3/Projects/GitHubAPI-Crawler/notebooks/2021-01-06/log.txt")
# gather_acc_sammple()
# with open("GitHub-data/assignment.txt") as f:
#     lines = f.read().splitlines()
#     lines = [l.split("\t")[0].replace(".py", ".ipynb") for l in lines]
# count_lines_multiple(lines)
# gather_top_nbs()
# gather_assignments("./GitHub-data")