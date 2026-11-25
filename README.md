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
	$ bundle config set path ~/.local/share/gem
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
- In posts, place the `<!--more-->` tag at the end of the excerpt of the post. The text up till there will appear on the "Latest news" section on the frontpae.
- Load media and special pages to `./assets/`

## Linux Package Repositories

The website hosts compliant static package repositories under `/repositories/` for Fedora (DNF), openSUSE (Zypper), Rocky Linux / RHEL (DNF), Debian (APT), and Ubuntu (APT).
To keep the git repository lightweight, package binaries (`.deb`, `.rpm`) are **not** stored here; only metadata referencing assets on GitHub Releases is generated.

### Adding New Packages (Release Updates)

When new releases of [Vega-Strike-Engine-Source](https://github.com/vegastrike/Vega-Strike-Engine-Source/releases) or [Assets-Production](https://github.com/vegastrike/Assets-Production/releases) are published:

#### Preferred Method: GitHub Actions Workflow
The repository update is fully automated via GitHub Actions:
1. Go to the repository's **Actions** tab on GitHub.
2. Select the **Update Linux Repositories** workflow from the left sidebar.
3. Click **Run workflow** &rarr; **Run workflow** on the `master` branch.
4. The workflow will query the GitHub Releases API, regenerate all repository metadata under `repositories/`, update `_data/repositories.json`, and commit the changes directly.

*(Note: The workflow also runs automatically on a weekly schedule every Sunday at 02:00 UTC).*

#### Alternative: Local Generation via Script
If you need to generate or test repository metadata locally:
1. Ensure Python 3 is installed.
2. Run the generator script:
   ```sh
   python3 scripts/generate_repositories.py --fetch --build
   ```
3. Commit and push the changes:
   ```sh
   git add _data/repositories.json _data/checksums_cache.json repositories/
   git commit -m "Update Linux repositories for release vX.Y.Z"
   git push
   ```
To rebuild metadata from cached static data without querying GitHub:
```sh
python3 scripts/generate_repositories.py --build
```

#### Checksums Cache (`_data/checksums_cache.json`)
Package SHA256 hashes are persisted in `_data/checksums_cache.json`. The generator only computes and rebuilds values if an entry is missing from the cache. If a hash is ever corrupted, maintainers can submit a PR removing that package's URL entry from `_data/checksums_cache.json`; the next run will automatically recompute and restore it.
