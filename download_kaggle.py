import os, sys
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

comps = api.competitions_list(sort_by="numberOfTeams")
comps = [str(c).split('/')[-1] for c in comps]
print(comps)
for comp in comps:
    path = os.path.join(".", "kaggle-notebooks", comp)
    if not os.path.exists(path):
        os.mkdir(path)
    nbs = api.kernels_list(competition=comp, sort_by="voteCount", language="python", page_size=50)
    nbs = [nb.ref[5:] for nb in nbs]
    for nb in nbs:
        api.kernels_pull(nb, path=path)