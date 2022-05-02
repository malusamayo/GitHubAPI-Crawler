# GitHubAPI-Crawler
This repository downloads data for evaluation.
- GitHub data: download repositories using `main.py`; extract notebooks using `gather-nbs.py`
- Kaggle data: download solutions using `download_kaggle.py`
- Data analysis: performed in `gather_info.py` and `result_analysis.ipynb`

Below are general instructions to use the crawler:
## To execute the script
Create token.txt file, and list your GitHub Token per line

main.py contains a few examples

## How to create GitHub Tokens
Once you log into your GitHub account, click on your avatar - Settings - Developer settings - Personal access tokens - Generate new token - Generate token (green button at the bottom of the screen). Important: DO NOT CHECK ANY OF THE BOXES THAT DEFINE SCOPES

You could have multiple email accounts (--> multiple GitHub accounts) --> make a token for each. 

## How to contribute
Create a fork, make changes in your fork, and once finish the implementation, submit a PR.


