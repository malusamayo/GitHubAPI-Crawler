import os, sys
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle.rest import ApiException
api = KaggleApi()
api.authenticate()

comps = api.competitions_list(sort_by="numberOfTeams")
comps = [str(c).split('/')[-1] for c in comps]
print(comps)
comps = ["house-prices-advanced-regression-techniques", "titanic"]
sort_by, postfix = "voteCount", "_voted"
for comp in comps:
    path = os.path.join(".", "kaggle-notebooks", comp + postfix)
    if not os.path.exists(path):
        os.mkdir(path)
    nbs = api.kernels_list(competition=comp, sort_by=sort_by, language="python", page=1, page_size=100)
    nbs += api.kernels_list(competition=comp, sort_by=sort_by, language="python", page=2, page_size=100)
    nbs = [nb.ref[5:] for nb in nbs]
    with open(os.path.join(".", "kaggle-notebooks", comp + postfix + ".txt"), "w") as f:
        f.write('\n'.join(nbs))
    for nb in nbs:
        try:
            api.kernels_pull(nb, path=os.path.join(path, nb))
        except ApiException:
            pass