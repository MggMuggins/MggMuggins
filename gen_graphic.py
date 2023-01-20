import json
from pathlib import Path
import requests
import subprocess
import yaml
import sys

from svgwrite.container import Group
from svgwrite.drawing import Drawing
from svgwrite.masking import Mask
from svgwrite.shapes import Circle, Rect
from svgwrite.text import Text, TSpan

import common

LINGUIST_LANGS = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"

EXCLUDE_EXTENSIONS = [".json", ".toml", ".bat"]

SVG_FILE = Path("graphic.svg")
BAR_HEIGHT = 20


def clean(s):
    return "".join([s.strip() for s in s.split('\n')])


def color_bar(svg, colors):
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
        rect.set_desc(lang)
        bar.add(rect)
        total_percent += percent

    other_percent = 100 - total_percent

    rect = Rect(
        size=(f"{other_percent}%", BAR_HEIGHT),
        insert=(f"{total_percent}%", 0),
        fill="gray",
    )
    rect.set_desc("Other")
    bar.add(rect)

    svg.add(bar)


def label(grp, circle_pos, lang, percent, color):
    grp.add(Circle(
        center=(10, circle_pos + 15),
        r=5,
        fill=color,
    ))
    txt = Text(
        "",
        insert=(20, circle_pos + 20),
    )
    txt.add(TSpan(
        lang,
        style="font-weight: bold;",
    ))
    txt.add(TSpan(
        f"{percent}%",
        style="fill: gray;",
    ))
    grp.add(txt)


def labels(svg, colors):
    """ Returns the minimum height of svg """

    labels = Group()

    circle_pos = BAR_HEIGHT
    total_percent = 0
    for percent, lang, color in colors:

        grp = Group()
        label(grp, circle_pos, lang, percent, color)
        labels.add(grp)

        circle_pos += 20
        total_percent += percent

    grp = Group()
    other_percent = round(100 - total_percent, 2)
    label(grp, circle_pos, "Other", other_percent, "gray")
    labels.add(grp)

    svg.add(labels)
    return circle_pos + 20


proc = subprocess.run(
    [
        "tokei",
        "--output=json",
        common.REPO_DIR,
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

colors = [(percent, lang, color) for lang, (percent, color) in colors.items()]
colors.sort()
colors.reverse()


svg = Drawing(SVG_FILE, size=("100%", 0))
color_bar(svg, colors)
new_height = labels(svg, colors)

svg['height'] = new_height
svg.save(pretty=True)

'''
with open(SVG_FILE, 'w') as svg_file:
    svg_file.write("""<ul style="list-style: none; padding-left: 0;">""")
    for percent, lang, color in colors:
        svg_file.write(language_list_elem(lang, percent, color))

    svg_file.write("""</ul>""")
'''
