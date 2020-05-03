# Vega Strike Project Front-page

This the source code for the Vega Strike Project Front-page. It is based on [Jekyll](https://jekyllrb.com/) static site generator and [Jekyll Doc Theme](https://github.com/aksakalli/jekyll-doc-theme/).

This README is for the future website maintainers. To learn how to use Jekyll, look at the official
documentation.

## Quick Start to see the website locally

- Install Ruby
- Exec:
	```sh
	$ gem install bundler jekyll
	$ cd vegastrike.github.io
	$ bundle install
	$ bundle exec jekyll serve
	```
- Browse to http://localhost:4000

## Notes

- Try to keep the repo as small as possible. No need to load huge files, unless they are going to be embedded directly into the website.
- To add a new link in the navigation bar, go to `_data/nav.yml`
- To change the theme, change the value of `bootwatch` in `_config.yml`
- To make a new announcement, add a file in `./_posts/`. E.g. `YYYY-MM-DD-name-of-post.md`. Added
to the top of the file the standard header as in all other posts.
- Load media to `./assets/`
