I wanted to get an idea of what code I've written and saved in the cloud.
High-level, the code in this repo downloads all the git repositories I own and
analyzes what programming languages they contain.

Of course, this doesn't reflect all the code I've ever written, but it gives
a general idea of what I've spent time with.

To generate the graphic (roughly):
- Find all my user's repositories from Github and Gitlab using their APIs
- Clone all the repos
- Run [`tokei`](https://github.com/XAMPPRocky/tokei) for language detection
- Grab `languages.yml` from [`linguist`](https://github.com/github/linguist)
  for colors
- Generate the graphic from the most common languages

Unfortunately Github doesn't allow SVGs to display tooltips; I haven't found
a way to display the language names with their colors and percentages nicely,
but if you're familiar with Github's language colors they are the same.

