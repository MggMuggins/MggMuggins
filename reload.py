"""
Reload the repos list (repos.json) and clone the repositories found.
"""

import itertools

from git import Repo
from pathlib import Path

import common

urls = common.reload_repos_list()

for repo_stat in itertools.chain(urls['github'], urls['gitlab']):
    repo_path = Path(common.REPO_DIR, repo_stat['name'])

    if not repo_path.exists():
        repo_path.mkdir(parents=True)

        print(f"Cloning from {repo_stat['url']} into ")
        repo = Repo.clone_from(
            url=repo_stat['url'],
            to_path=repo_path,
        )
    else:
        # TODO: Pull
        # Repo(repo_path)
