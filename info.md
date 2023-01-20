Unfortunately Github doesn't allow SVGs to display tooltips; I haven't found
a way to display the language names with their colors and percentages nicely,
but if you're familiar with Github's language colors they are the same.

To generate the graphic (roughly):
- Find all my user's repositories from Github and Gitlab using their APIs
- Clone all the repos
- Run [`tokei`](https://github.com/XAMPPRocky/tokei) for language detection
- Grab `languages.yml` from [`linguist`](https://github.com/github/linguist)
  for colors
- Generate the graphic from the most common languages
