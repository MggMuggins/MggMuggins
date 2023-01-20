import argparse
import json
import requests
import subprocess
import sys
import yaml

from git import Repo
from pathlib import Path

from svgwrite.container import Group
from svgwrite.drawing import Drawing
from svgwrite.masking import Mask
from svgwrite.shapes import Rect


USER = "MggMuggins"

REPO_DIR = Path('repos')
REPO_FILE = Path('repos.json')
SVG_FILE = Path("languages.svg")
# STAT_FILE = Path('stats.json')

LINGUIST_LANGS = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"

EXCLUDE_EXTENSIONS = [".json", ".toml", ".bat"]

BAR_HEIGHT = 20


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
    """
    Reload repos.json from Gitlab & Github
    """
    urls = fetch_github() + fetch_gitlab()

    with open(url_file_path, 'w') as url_file:
        json.dump(urls, url_file, indent=4)

    return urls


def load_repos_list(url_file_path):
    """
    Load repos.json
    """
    if not url_file_path.exists():
        urls = reload_repos_list(url_file_path)
    else:
        with open(url_file_path, 'r') as url_file:
            urls = json.load(url_file)
    return urls


def update_repos(urls):
    """
    Clone/update the repositories given in urls (list of dicts)
    """
    for repo_info in urls:
        repo_path = Path(REPO_DIR, repo_info['name'])

        if not repo_path.exists():
            repo_path.mkdir(parents=True)

            print(f"Cloning from {repo_info['url']} into {repo_path}")
            repo = Repo.clone_from(
                url=repo_info['url'],
                to_path=repo_path,
            )
        else:
            repo = Repo(repo_path)
            print(f"{repo_path} pull origin")
            repo.remotes.origin.pull()


def gen_percentages():
    """
    Returns a dict mapping language (str) to percentage (float). Runs tokei.
    """
    proc = subprocess.run(
        [
            "tokei",
            "--output=json",
            REPO_DIR,
        ] + ["--exclude=*" + exclude for exclude in EXCLUDE_EXTENSIONS],
        capture_output=True,
    )

    try:
        repo_info = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("Tokei returned invalid json:")
        print(proc.stdout)
        print(proc.stderr)
        sys.exit(1)

    total = repo_info.pop("Total")
    print(f"Total code lines: {total['code']}")

    percentages = {}

    for lang_name, info in repo_info.items():
        print(f"{lang_name} code lines: {info['code']}")
        percentage = info["code"] / total["code"]

        if percentage >= 0.005:
            percentages[lang_name] = round(percentage * 100, 1)

    return percentages


def add_colors(percentages):
    ling_resp = requests.get(LINGUIST_LANGS)
    ling_langs = yaml.safe_load(ling_resp.content)

    aliases = {}
    for lang, info in ling_langs.items():
        aliases[lang.lower()] = lang

        if "aliases" in info:
            for alias in info["aliases"]:
                aliases[alias.lower()] = lang

    colors = {}
    for lang, percent in percentages.items():
        lang = aliases[lang.lower()]
        color = ling_langs[lang]['color']

        if lang not in colors:
            colors[lang] = (percent, color)
        else:
            other_pcnt, _ = colors[lang]
            colors[lang] = (other_pcnt + percent, color)

    colors = [
        (percent, lang, color)
        for lang, (percent, color) in colors.items()
    ]
    colors.sort()
    colors.reverse()
    return colors


def write_color_bar(colors):
    """
    Create graphic.svg based on a list of language info. `colors` is a list
    of `(percent: float, language_name: str, hex_color: str)`
    """
    svg = Drawing(SVG_FILE, size=("100%", BAR_HEIGHT))

    bar_mask = Mask(id="bar_mask")
    bar_mask.add(Rect(
        size=("100%", BAR_HEIGHT),
        rx=BAR_HEIGHT / 2,
        ry=BAR_HEIGHT / 2,
        fill="white",
    ))
    svg.defs.add(bar_mask)

    bar = Group(
        # size=("100%", BAR_HEIGHT),
        mask="url(#bar_mask)"
    )

    total_percent = 0
    for percent, lang, color in colors:
        print(f"{lang}: {percent}% {color}")

        rect = Rect(
            size=(f"{percent}%", BAR_HEIGHT),
            insert=(f"{total_percent}%", 0),
            fill=color,
        )
        rect.set_desc(f"{lang} {percent}%")
        bar.add(rect)
        total_percent += percent

    other_percent = 100 - total_percent

    rect = Rect(
        size=(f"{other_percent}%", BAR_HEIGHT),
        insert=(f"{total_percent}%", 0),
        fill="gray",
    )
    rect.set_desc(f"Other {other_percent}%")
    bar.add(rect)

    svg.add(bar)
    svg.save(pretty=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="language_color_bar",
        description="Draw a Github-style language summary color bar for some repos",
    )
    parser.add_argument(
        "--fetch",
        help="Reload repos.json and clone/update the repos",
        action='store_true',
    )

    args = parser.parse_args()

    if args.fetch:
        urls = reload_repos_list(REPO_FILE)
        update_repos(urls)

    colors = add_colors(gen_percentages())
    write_color_bar(colors)
