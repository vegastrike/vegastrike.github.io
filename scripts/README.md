# Vega Strike Linux Repositories Infrastructure

This directory contains the automation and generator scripts for managing Vega Strike's Linux package repositories.

## Overview

The Linux package repositories are hosted statically under `/repositories/` on `https://www.vega-strike.org/`.
They support:
- **Fedora** (DNF / RPM): Fedora 40, 41, 42, 43, 44 (`x86_64`)
- **openSUSE** (Zypper / YaST / RPM): Leap 15.6, 16.0 (`x86_64`)
- **Rocky Linux / RHEL / CentOS** (DNF / RPM): 8, 9, 10 (`x86_64`)
- **Debian** (APT): Bookworm (12), Trixie (13) (`amd64`, `all`)
- **Ubuntu & Linux Mint** (APT): Jammy (22.04), Noble (24.04), Resolute (26.04) (`amd64`, `all`)

## Design Principles

1. **Zero Binary Storage in Git**: Package files (`.rpm`, `.deb`) are NOT stored in the website's git repository. Instead, repository metadata (`primary.xml.gz`, `repomd.xml`, `Packages.gz`, `Release`) references the binaries directly on GitHub Releases (`https://github.com/vegastrike/.../releases/download/...`).
2. **Compliant Tooling**: Standard system tools (`dnf`, `zypper`, `yast`, `apt`) download and verify the packages directly from GitHub's CDN.
3. **Decoupled Yet Jointly Deployed**: Jekyll operates normally and treats `/repositories/` as static assets. When Jekyll compiles the site into `_site/`, both the website and the repository metadata are packaged together seamlessly.

## Usage

### Updating Repositories Locally

To fetch the latest release metadata from GitHub Releases and regenerate the repository tree:

```bash
python3 scripts/generate_repositories.py --fetch --build
```

To build repository metadata using the cached data file (`_data/repositories.json`) without hitting the GitHub API:

```bash
python3 scripts/generate_repositories.py --build
```

### Automated Updates

The GitHub Actions workflow `.github/workflows/update_repositories.yml` runs weekly and can also be triggered manually via `workflow_dispatch` to keep repository metadata in sync with new Vega Strike releases.

### Checksums Cache (`_data/checksums_cache.json`)

Package SHA256 checksums are tracked persistently in `_data/checksums_cache.json`:
- For modern releases where GitHub Releases supplies a native `digest`, the native SHA256 digest is used.
- For releases where GitHub does not provide a native `digest`, the generator checks `_data/checksums_cache.json`.
- The generator only computes and rebuilds checksum values if an entry is missing from the cache.

> [!NOTE]
> **Maintainer Guide for Rebuilding Hashes**:
> If a package's checksum in the cache ever becomes corrupted or needs to be refreshed, simply submit a Pull Request deleting that package's download URL entry from `_data/checksums_cache.json`.
> On the next run of the generator (or weekly workflow run), the generator will detect that the entry is missing from the cache and will automatically re-download, recompute, and restore the verified hash.
