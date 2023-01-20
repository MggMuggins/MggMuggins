from pathlib import Path

README_TEMPLATE = Path('template.md')
README_PATH = Path('README.md')

GRAPHIC_PATH = Path('graphic.html')

with (
    open(README_TEMPLATE, 'r') as template,
    open(GRAPHIC_PATH, 'r') as graphic,
    open(README_PATH, 'w') as readme,
):
    template = template.read()
    graphic = graphic.read()

    content = template.format(graphic)

    readme.write(content)
