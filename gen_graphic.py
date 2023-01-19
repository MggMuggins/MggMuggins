import json
from pathlib import Path
import requests
import subprocess
import yaml

import common

LINGUIST_LANGS = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"

SVG_FILE = Path("graphic.svg")
SVG_START = """
<svg version="1.1"
     width="500" height="200"
     xmlns="http://www.w3.org/2000/svg">
"""
SVG_END = """
</svg>
"""


proc = subprocess.run(
    ["tokei", "--output=json", common.REPO_DIR],
    capture_output=True,
)
repo_info = json.loads(proc.stdout)

total = repo_info.pop("Total")
print(f"Total code lines: {total['code']}")

percentages = {}

for lang_name, info in repo_info.items():
    print(f"{lang_name} code lines: {info['code']}")
    percentage = info["code"] / total["code"]

    if percentage >= 0.01:
        percentages[lang_name] = round(percentage * 100, 1)

print(json.dumps(percentages, indent=4))

ling_resp = requests.get(LINGUIST_LANGS)
ling_langs = yaml.safe_load(ling_resp.content)

aliases = {}
for lang, info in ling_langs.items():
    aliases[lang.lower()] = lang

    if "aliases" in info:
        for alias in info["aliases"]:
            aliases[alias.lower()] = lang

with open(SVG_FILE, 'w') as svg_file:
    svg_file.write(SVG_START)

    pos = 0
    for lang, percent in percentages.items():
        lang = aliases[lang.lower()]
        lang_color = ling_langs[lang]['color']
        print(f"{lang}: {percent}% {lang_color}")

        svg_file.write(f"""
            <rect x="{pos}%" width="{percent}" height="10%" fill="{lang_color}" />
        """)
        pos += 10

    svg_file.write(SVG_END)
