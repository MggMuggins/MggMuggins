import json
import requests
import sys

from pathlib import Path

USER = "MggMuggins"
REPO_DIR = Path('repos')
REPO_FILE = Path('repos.json')
STAT_FILE = Path('stats.json')


def fetch_github():
    github_url = f"https://api.github.com/users/{USER}/repos"

    github_resp = requests.get(github_url)
    github_resp.raise_for_status()

    github_repos = json.loads(github_resp.content)

    github_urls = [
        {'name': repo['name'], 'url': repo['html_url']}
        for repo in github_repos
        if not repo['fork']
    ]

    print(f"Got urls from github:\n{github_urls}")

    return github_urls


def fetch_gitlab():
    gitlab_url = f"https://gitlab.com/api/v4/users/{USER}/projects"

    gitlab_resp = requests.get(gitlab_url)
    gitlab_resp.raise_for_status()

    gitlab_repos = json.loads(gitlab_resp.content)

    gitlab_urls = [
        {'name': repo['name'], 'url': repo['web_url']}
        for repo in gitlab_repos
        if 'forked_from_project' not in repo
    ]

    print(f"Got urls from gitlab:\n{gitlab_urls}")

    return gitlab_urls


def reload_repos_list(url_file_path):
    urls = {
        'github': fetch_github(),
        'gitlab': fetch_gitlab(),
    }

    with open(url_file_path, 'w') as url_file:
        json.dump(urls, url_file, indent=4)

    return urls


def fetch_repos_list():
    if not REPO_FILE.exists():
        urls = reload_repos_list(REPO_FILE)
    else:
        with open(REPO_FILE, 'r') as url_file:
            urls = json.load(url_file)
    return urls


def stat_file_path(repo_name):
    path = Path(REPO_DIR, repo_name)
    return path.with_suffix(".json")


if __name__ == "__main__":
    print("This file is a library")
    sys.exit(1)
