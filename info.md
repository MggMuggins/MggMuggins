To generate the graphic on my profile README (roughly):
- Find all my user's repositories from Github and Gitlab using their APIs
- Clone all the repos into `repos/`
- Run [`tokei`](https://github.com/XAMPPRocky/tokei) for language detection
- Grab `languages.yml` from [`linguist`](https://github.com/github/linguist)
  for colors
- Generate the graphic from the most common languages
