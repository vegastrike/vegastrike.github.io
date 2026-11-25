#!/usr/bin/env python3
"""
Vega Strike Linux Repositories Generator
-----------------------------------------
Generates compliant, static Linux package repositories for:
  - Fedora (DNF / RPM)
  - openSUSE (Zypper / YaST / RPM)
  - Rocky Linux / RHEL / CentOS (DNF / RPM)
  - Debian & Ubuntu (APT / DEB)

Supports both:
  - Stable Channel: official non-prerelease versions (e.g. 0.9.1, 0.9.0, 0.8.0...)
  - Testing Channel: pre-release builds (e.g. 0.10.x and 0.11.x alphas/betas)

The metadata files point to assets hosted on GitHub Releases,
avoiding the need to store large binaries in the git repository.
"""

import os
import sys
import re
import json
import gzip
import hashlib
import shutil
import argparse
from datetime import datetime, timezone
import urllib.request

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(WORKSPACE_DIR, "_data")
REPOS_DIR = os.path.join(WORKSPACE_DIR, "repositories")
DATA_FILE = os.path.join(DATA_DIR, "repositories.json")
CHECKSUMS_FILE = os.path.join(DATA_DIR, "checksums_cache.json")

VSE_API_URL = "https://api.github.com/repos/vegastrike/Vega-Strike-Engine-Source/releases?per_page=100"
ASSETS_API_URL = "https://api.github.com/repos/vegastrike/Assets-Production/releases?per_page=100"
VSUBP_API_URL = "https://api.github.com/repos/vegastrike/vsu-black-paralysis/releases?per_page=100"

def load_checksums_cache():
    if os.path.exists(CHECKSUMS_FILE):
        try:
            with open(CHECKSUMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load checksums cache: {e}", file=sys.stderr)
    return {}

def save_checksums_cache(cache):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CHECKSUMS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)

def get_asset_sha256(asset, cache, download_if_missing=True):
    # 1. Native digest from GitHub Release API
    digest = asset.get("digest")
    if digest and digest.startswith("sha256:"):
        sha = digest[7:]
        url = asset.get("browser_download_url", "")
        if url and cache is not None:
            cache[url] = sha
        return sha

    url = asset.get("browser_download_url", "")
    # 2. Persistent checksum cache
    if cache is not None and url and url in cache and cache[url]:
        return cache[url]

    # 3. Compute on demand if missing from cache
    if download_if_missing and url:
        try:
            print(f"Computing missing SHA256 for {asset.get('name', url)}...")
            req = urllib.request.Request(url, headers={"User-Agent": "VegaStrike-Repo-Generator"})
            h = hashlib.sha256()
            with urllib.request.urlopen(req) as resp:
                while chunk := resp.read(4 * 1024 * 1024):
                    h.update(chunk)
            sha = h.hexdigest()
            if cache is not None:
                cache[url] = sha
                save_checksums_cache(cache)
            return sha
        except Exception as e:
            print(f"Warning: Failed to compute SHA256 for {url}: {e}", file=sys.stderr)

    return ""

def fetch_github_releases(url):
    print(f"Fetching releases from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "VegaStrike-Repo-Generator"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching from {url}: {e}", file=sys.stderr)
        return []

def parse_package_asset(asset, release_tag, repo_source, is_prerelease=False, cache=None):
    filename = asset.get("name", "")
    if not (filename.endswith(".deb") or filename.endswith(".rpm")):
        return None

    size = asset.get("size", 0)
    download_url = asset.get("browser_download_url", "")
    sha256 = get_asset_sha256(asset, cache) if cache is not None else ""

    # Engine packages:
    # Supports 0.6.x, 0.7.x, 0.8.x, 0.9.x, 0.10.x, 0.11.x, etc.
    # e.g.: Vega-Strike_v0.11.0-alpha2-GLVND-fedora-43_x86_64.rpm
    #       Vega-Strike_0.8.0-alpha3-543b3fb719000c1bafe7ace3abd42247460d7470-py3-GLVND-Debian-bullseye_x86_64.deb
    #       Vega-Strike_v0.7.0-py3-fedora-33_x86_64.rpm
    #       vega-strike_v0.6.0-Ubuntu-xenial_x86_64.deb
    m_vse = re.match(
        r"^[Vv]ega-[Ss]trike_v?([0-9a-zA-Z\.\-]+?)-(?:[0-9a-f]{40}-)?(?:(py[23])-)?(?:(GLVND|LEGACY)-)?([A-Za-z]+)-([0-9a-zA-Z\.\-]+)_([0-9a-zA-Z_]+)\.(deb|rpm)$",
        filename
    )
    if m_vse:
        ver, py, opengl, distro_raw, dist_ver_raw, arch, pkg_type = m_vse.groups()
        distro = distro_raw.lower()
        if distro == "centos":
            distro = "rocky"
        dist_ver = dist_ver_raw.lower()
        if dist_ver.startswith("leap-"):
            dist_ver = dist_ver.replace("leap-", "")

        return {
            "component": "engine",
            "package_name": "vegastrike",
            "display_name": "Vega Strike Engine",
            "version": ver,
            "opengl": opengl or "default",
            "distro": distro,
            "distro_version": dist_ver,
            "arch": "amd64" if arch == "x86_64" and pkg_type == "deb" else arch,
            "pkg_type": pkg_type,
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source,
            "prerelease": is_prerelease
        }

    # Assets packages (RPM):
    # e.g.: vsUTCS_0.10.0-alpha3-fedora-42.rpm
    #       vsUTCS_0.10.0-alpha3-opensuse-leap-16.0.rpm
    #       vsUTCS_v0.9.1-rocky-9.5.rpm
    #       vsUTCS_v0.6.0-centos-8.rpm
    m_asset_rpm = re.match(
        r"^vsUTCS[_-]v?([0-9a-zA-Z\.\-]+?)-([a-zA-Z\-]+)-([0-9a-zA-Z\.\-]+)\.rpm$",
        filename
    )
    if m_asset_rpm:
        ver, distro_raw, dist_ver_raw = m_asset_rpm.groups()
        distro = distro_raw.lower()
        if distro == "centos":
            distro = "rocky"
        dist_ver = dist_ver_raw.lower()
        if distro.startswith("opensuse"):
            distro = "opensuse"
            dist_ver = dist_ver.replace("leap-", "")

        return {
            "component": "assets",
            "package_name": "vsutcs",
            "provides": ["vegastrike-upon-the-coldest-sea", "vsUTCS"],
            "display_name": "Vega Strike: Upon The Coldest Sea Assets",
            "version": ver,
            "opengl": "any",
            "distro": distro,
            "distro_version": dist_ver,
            "arch": "noarch",
            "pkg_type": "rpm",
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source,
            "prerelease": is_prerelease
        }

    # Assets packages (DEB):
    # e.g.: vsUTCS_0.10.0-alpha3.deb
    #       vsUTCS-0.6.0-Linux.deb
    #       vsUTCS_v0.7.0.deb
    m_asset_deb = re.match(r"^vsUTCS[_-]v?([0-9a-zA-Z\.\-]+?)(?:-Linux)?\.deb$", filename)
    if m_asset_deb:
        ver = m_asset_deb.group(1)
        return {
            "component": "assets",
            "package_name": "vsutcs",
            "provides": ["vegastrike-upon-the-coldest-sea"],
            "display_name": "Vega Strike: Upon The Coldest Sea Assets",
            "version": ver,
            "opengl": "any",
            "distro": "debian",  # shared across debian/ubuntu/mint
            "distro_version": "all",
            "arch": "all",
            "pkg_type": "deb",
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source,
            "prerelease": is_prerelease
        }

    # Black Paralysis Assets (RPM):
    # e.g.: vsuBP_0.1.3-fedora-43.rpm
    #       vsuBP_0.1.3-opensuse-leap-16.0.rpm
    #       vsuBP_0.1.3-rocky-10.2.rpm
    #       vsuBP_v0.1.1-fedora-43.rpm
    m_vsubp_rpm = re.match(
        r"^vsuBP[_-]v?([0-9a-zA-Z\.\-]+?)-([a-zA-Z\-]+)-([0-9a-zA-Z\.\-]+)\.rpm$",
        filename
    )
    if m_vsubp_rpm:
        ver, distro_raw, dist_ver_raw = m_vsubp_rpm.groups()
        distro = distro_raw.lower()
        if distro == "centos":
            distro = "rocky"
        dist_ver = dist_ver_raw.lower()
        if distro.startswith("opensuse"):
            distro = "opensuse"
            dist_ver = dist_ver.replace("leap-", "")

        return {
            "component": "assets",
            "package_name": "vsuBP",
            "provides": ["vsu-black-paralysis", "vsubp"],
            "display_name": "VSU: Black Paralysis Assets",
            "version": ver,
            "opengl": "any",
            "distro": distro,
            "distro_version": dist_ver,
            "arch": "noarch",
            "pkg_type": "rpm",
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source,
            "prerelease": is_prerelease
        }

    # Black Paralysis Assets (DEB):
    # e.g.: vsubp_0.1.3.deb
    #       vsubp_v0.1.1.deb
    m_vsubp_deb = re.match(r"^vsubp[_-]v?([0-9a-zA-Z\.\-]+?)(?:-Linux)?\.deb$", filename)
    if m_vsubp_deb:
        ver = m_vsubp_deb.group(1)
        return {
            "component": "assets",
            "package_name": "vsubp",
            "provides": ["vsu-black-paralysis"],
            "display_name": "VSU: Black Paralysis Assets",
            "version": ver,
            "opengl": "any",
            "distro": "debian",  # shared across debian/ubuntu/mint
            "distro_version": "all",
            "arch": "all",
            "pkg_type": "deb",
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source,
            "prerelease": is_prerelease
        }

    return None

def collect_release_data():
    cache = load_checksums_cache()
    vse_releases = fetch_github_releases(VSE_API_URL)
    assets_releases = fetch_github_releases(ASSETS_API_URL)
    vsubp_releases = fetch_github_releases(VSUBP_API_URL)

    packages = []
    seen_urls = set()

    for r in vse_releases:
        tag = r.get("tag_name", "")
        is_pre = r.get("prerelease", False)
        for a in r.get("assets", []):
            pkg = parse_package_asset(a, tag, "Vega-Strike-Engine-Source", is_pre, cache)
            if pkg and pkg["download_url"] not in seen_urls:
                packages.append(pkg)
                seen_urls.add(pkg["download_url"])

    for r in assets_releases:
        tag = r.get("tag_name", "")
        is_pre = r.get("prerelease", False)
        for a in r.get("assets", []):
            pkg = parse_package_asset(a, tag, "Assets-Production", is_pre, cache)
            if pkg and pkg["download_url"] not in seen_urls:
                packages.append(pkg)
                seen_urls.add(pkg["download_url"])

    for r in vsubp_releases:
        tag = r.get("tag_name", "")
        is_pre = r.get("prerelease", False)
        for a in r.get("assets", []):
            pkg = parse_package_asset(a, tag, "vsu-black-paralysis", is_pre, cache)
            if pkg and pkg["download_url"] not in seen_urls:
                packages.append(pkg)
                seen_urls.add(pkg["download_url"])

    save_checksums_cache(cache)
    return packages

def generate_rpm_repodata(output_dir, packages_list):
    """
    Generates repomd.xml and primary.xml.gz inside output_dir/repodata/
    pointing directly to package URLs on GitHub Releases.
    """
    if not packages_list:
        return

    repodata_dir = os.path.join(output_dir, "repodata")
    os.makedirs(repodata_dir, exist_ok=True)

    now_ts = int(datetime.now(timezone.utc).timestamp())

    # Build primary.xml content
    primary_xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<metadata xmlns="http://linux.duke.edu/metadata/common" xmlns:rpm="http://linux.duke.edu/metadata/rpm" packages="{len(packages_list)}">'
    ]

    for p in packages_list:
        pkg_name = p["package_name"]
        arch = p["arch"]
        ver = p["version"].replace("-", ".")
        sha256 = p["sha256"] or "0" * 64
        size = p["size"]
        url = p["download_url"]
        summary = p["display_name"]
        if p["package_name"] == "vegastrike":
            description = "Vega Strike 3D Space Flight Simulator"
        elif p["package_name"] == "vsutcs":
            description = "Vega Strike Upon the Coldest Sea Game Data"
        elif p["package_name"].lower() in ("vsubp", "vsu-black-paralysis"):
            description = "VSU Black Paralysis Game Data"
        else:
            description = p.get("display_name", "")

        primary_xml_lines.append(f'  <package type="rpm">')
        primary_xml_lines.append(f'    <name>{pkg_name}</name>')
        primary_xml_lines.append(f'    <arch>{arch}</arch>')
        primary_xml_lines.append(f'    <version epoch="0" ver="{ver}" rel="1"/>')
        primary_xml_lines.append(f'    <checksum type="sha256" pkgid="YES">{sha256}</checksum>')
        primary_xml_lines.append(f'    <summary>{summary}</summary>')
        primary_xml_lines.append(f'    <description>{description}</description>')
        primary_xml_lines.append(f'    <packager>Vega Strike Team</packager>')
        primary_xml_lines.append(f'    <url>https://www.vega-strike.org</url>')
        primary_xml_lines.append(f'    <time file="{now_ts}" build="{now_ts}"/>')
        primary_xml_lines.append(f'    <size package="{size}" installed="{size}" archive="{size}"/>')
        primary_xml_lines.append(f'    <location href="{url}"/>')
        primary_xml_lines.append(f'    <format>')
        primary_xml_lines.append(f'      <rpm:license>GPLv2+</rpm:license>')
        primary_xml_lines.append(f'      <rpm:vendor>Vega Strike</rpm:vendor>')
        primary_xml_lines.append(f'      <rpm:group>Amusements/Games</rpm:group>')
        primary_xml_lines.append(f'      <rpm:provides>')
        primary_xml_lines.append(f'        <rpm:entry name="{pkg_name}" flags="EQ" epoch="0" ver="{ver}" rel="1"/>')
        for prov in p.get("provides", []):
            if prov != pkg_name:
                primary_xml_lines.append(f'        <rpm:entry name="{prov}" flags="EQ" epoch="0" ver="{ver}" rel="1"/>')
        primary_xml_lines.append(f'      </rpm:provides>')
        primary_xml_lines.append(f'    </format>')
        primary_xml_lines.append(f'  </package>')

    primary_xml_lines.append('</metadata>\n')
    primary_xml_bytes = "\n".join(primary_xml_lines).encode("utf-8")
    primary_open_checksum = hashlib.sha256(primary_xml_bytes).hexdigest()
    primary_open_size = len(primary_xml_bytes)

    primary_gz_path = os.path.join(repodata_dir, "primary.xml.gz")
    with gzip.open(primary_gz_path, "wb") as f_gz:
        f_gz.write(primary_xml_bytes)

    with open(primary_gz_path, "rb") as f_check:
        primary_gz_bytes = f_check.read()
    primary_gz_checksum = hashlib.sha256(primary_gz_bytes).hexdigest()
    primary_gz_size = len(primary_gz_bytes)

    # Build repomd.xml
    repomd_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<repomd xmlns="http://linux.duke.edu/metadata/repo" xmlns:rpm="http://linux.duke.edu/metadata/rpm">
  <data type="primary">
    <checksum type="sha256">{primary_gz_checksum}</checksum>
    <open-checksum type="sha256">{primary_open_checksum}</open-checksum>
    <location href="repodata/primary.xml.gz"/>
    <timestamp>{now_ts}</timestamp>
    <size>{primary_gz_size}</size>
    <open-size>{primary_open_size}</open-size>
  </data>
</repomd>
"""
    with open(os.path.join(repodata_dir, "repomd.xml"), "w", encoding="utf-8") as f_repomd:
        f_repomd.write(repomd_xml)

def generate_deb_repository(output_dir, suite, components_pkgs, distro_label="Debian"):
    """
    components_pkgs: dict like {"main": [pkgs], "testing": [pkgs]}
    Generates dists/<suite>/Release and dists/<suite>/<comp>/binary-<arch>/Packages[.gz]
    """
    dists_suite_dir = os.path.join(output_dir, "dists", suite)
    os.makedirs(dists_suite_dir, exist_ok=True)

    # Clean up obsolete components and architecture subdirectories
    for comp_name in ["main", "testing"]:
        comp_dir = os.path.join(dists_suite_dir, comp_name)
        pkgs = components_pkgs.get(comp_name, [])
        if not pkgs:
            if os.path.exists(comp_dir):
                shutil.rmtree(comp_dir)
            continue

        active_arches = set(p["arch"] for p in pkgs)
        if os.path.exists(comp_dir):
            for entry in os.listdir(comp_dir):
                if entry.startswith("binary-"):
                    arch_part = entry.replace("binary-", "")
                    if arch_part not in active_arches:
                        shutil.rmtree(os.path.join(comp_dir, entry))

    release_files_meta = []
    all_architectures = set()

    for comp_name, pkgs in components_pkgs.items():
        if not pkgs:
            continue
        arch_map = {}
        for p in pkgs:
            arch = p["arch"]
            arch_map.setdefault(arch, []).append(p)
            all_architectures.add(arch)

        for arch, arch_pkgs in arch_map.items():
            bin_dir = os.path.join(dists_suite_dir, comp_name, f"binary-{arch}")
            os.makedirs(bin_dir, exist_ok=True)

            pkg_entries = []
            for p in arch_pkgs:
                ver = p["version"].replace("-", "~")
                sha256 = p["sha256"] or "0" * 64
                size = p["size"]
                installed_size = max(1, size // 1024)
                entry = [
                    f"Package: {p['package_name']}",
                    f"Version: {ver}-1",
                    f"Architecture: {arch}",
                    f"Maintainer: Vega Strike Development Team <maintainer@vega-strike.org>",
                    f"Installed-Size: {installed_size}",
                    f"Filename: {p['download_url']}",
                    f"Size: {size}",
                    f"SHA256: {sha256}",
                    f"Section: games",
                    f"Priority: optional",
                ]
                if p.get("provides"):
                    entry.append(f"Provides: {', '.join(p['provides'])}")
                entry.extend([
                    f"Homepage: https://www.vega-strike.org",
                    f"Description: {p['display_name']}",
                    f" Vega Strike is an Open Source 3D Action-Space-Sim that lets you trade,",
                    f" fight, and explore in a vast universe."
                ])
                pkg_entries.append("\n".join(entry))

            packages_content = ("\n\n".join(pkg_entries) + "\n").encode("utf-8")

            pkgs_path = os.path.join(bin_dir, "Packages")
            with open(pkgs_path, "wb") as f_pkg:
                f_pkg.write(packages_content)

            pkgs_gz_path = os.path.join(bin_dir, "Packages.gz")
            with gzip.open(pkgs_gz_path, "wb") as f_gz:
                f_gz.write(packages_content)

            rel_pkgs_path = f"{comp_name}/binary-{arch}/Packages"
            rel_pkgs_gz_path = f"{comp_name}/binary-{arch}/Packages.gz"

            with open(pkgs_gz_path, "rb") as f_gz_read:
                gz_bytes = f_gz_read.read()

            release_files_meta.append((rel_pkgs_path, len(packages_content), hashlib.md5(packages_content).hexdigest(), hashlib.sha256(packages_content).hexdigest()))
            release_files_meta.append((rel_pkgs_gz_path, len(gz_bytes), hashlib.md5(gz_bytes).hexdigest(), hashlib.sha256(gz_bytes).hexdigest()))

    active_components = [c for c, pkgs in components_pkgs.items() if pkgs]
    if not active_components:
        return

    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    release_lines = [
        f"Origin: Vega Strike",
        f"Label: Vega Strike {distro_label} Repository",
        f"Suite: {suite}",
        f"Codename: {suite}",
        f"Components: {' '.join(sorted(active_components))}",
        f"Architectures: {' '.join(sorted(all_architectures))}",
        f"Description: Vega Strike Official Packages for {distro_label} ({suite})",
        f"Date: {date_str}",
        f"MD5Sum:"
    ]
    for rel_path, fsize, fmd5, fsha256 in release_files_meta:
        release_lines.append(f" {fmd5} {fsize} {rel_path}")

    release_lines.append("SHA256:")
    for rel_path, fsize, fmd5, fsha256 in release_files_meta:
        release_lines.append(f" {fsha256} {fsize} {rel_path}")

    with open(os.path.join(dists_suite_dir, "Release"), "w", encoding="utf-8") as f_rel:
        f_rel.write("\n".join(release_lines) + "\n")

def generate_landing_page(packages):
    """
    Generates a responsive repositories/index.html page with copy-paste instructions
    for Stable and Testing channels across all supported distributions.
    """
    now_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vega Strike - Linux Package Repositories</title>
  <link rel="stylesheet" href="/assets/css/bootstrap.min.css">
  <link rel="stylesheet" href="/assets/css/main.css">
  <style>
    body {{
      background-color: #060606;
      color: #e0e0e0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .repo-header {{
      background: linear-gradient(180deg, #181c24 0%, #0d0f12 100%);
      border-bottom: 1px solid #2a313d;
      padding: 40px 0 30px;
      margin-bottom: 30px;
    }}
    .repo-card {{
      background: #14171d;
      border: 1px solid #272d38;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
      transition: border-color 0.2s ease;
    }}
    pre.code-block {{
      background: #090a0d;
      border: 1px solid #222630;
      border-radius: 6px;
      color: #79c0ff;
      padding: 14px;
      font-size: 0.9em;
      position: relative;
      overflow-x: auto;
    }}
    .btn-copy {{
      position: absolute;
      top: 8px;
      right: 8px;
      background: #21262d;
      border: 1px solid #363b42;
      color: #c9d1d9;
      font-size: 0.75em;
      padding: 3px 8px;
      border-radius: 4px;
      cursor: pointer;
    }}
    .btn-copy:hover {{
      background: #30363d;
      color: #fff;
    }}
    .nav-tabs > li > a {{
      color: #8b949e;
      background: transparent;
      border: 1px solid transparent;
      font-weight: 600;
    }}
    .nav-tabs > li.active > a, .nav-tabs > li.active > a:focus, .nav-tabs > li.active > a:hover {{
      color: #58a6ff;
      background-color: #14171d;
      border: 1px solid #272d38;
      border-bottom-color: transparent;
    }}
    .tab-content {{
      background: #14171d;
      border: 1px solid #272d38;
      border-top: none;
      border-radius: 0 0 8px 8px;
      padding: 24px;
    }}
    .channel-box {{
      background: #0e1117;
      border: 1px solid #272d38;
      border-radius: 6px;
      padding: 18px;
      margin-top: 15px;
      margin-bottom: 20px;
    }}
    .channel-title {{
      font-size: 1.1em;
      font-weight: 600;
      margin-top: 0;
      margin-bottom: 10px;
    }}
    .channel-stable {{ border-left: 4px solid #2ea043; }}
    .channel-testing {{ border-left: 4px solid #dbab09; }}
    a.site-nav {{
      color: #58a6ff;
      text-decoration: none;
    }}
    a.site-nav:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <div class="repo-header">
    <div class="container">
      <p><a href="/" class="site-nav">&larr; Back to Vega Strike Home</a> | <a href="/install/" class="site-nav">Installation Guide</a></p>
      <h1>Vega Strike Linux Repositories</h1>
      <p class="lead" style="color: #8b949e;">Official static repositories for Fedora, openSUSE, Rocky Linux / RHEL, Debian, and Ubuntu.</p>
      <small style="color: #6e7681;">Updated: {now_date} &bull; Packages served directly from GitHub Releases CDN</small>
    </div>
  </div>

  <div class="container" style="padding-bottom: 60px;">
    
    <div class="alert alert-info" style="background-color: #0d2238; border-color: #1f4266; color: #a5d6ff;">
      <strong>Note:</strong> Vega Strike provides two release channels:
      <ul style="margin-top: 8px; margin-bottom: 8px;">
        <li><strong style="color: #56d364;">Stable Channel (Default):</strong> Official releases (e.g. 0.9.1, 0.9.0, 0.8.0). Enabled by default.</li>
        <li><strong style="color: #e3b341;">Testing Channel (Opt-in):</strong> Latest preview alphas and betas (e.g. 0.10.x, 0.11.x). Disabled by default.</li>
      </ul>
      <strong>Available Packages:</strong>
      <ul style="margin-top: 4px; margin-bottom: 0;">
        <li><code>vegastrike</code> &mdash; Core Game Engine</li>
        <li><code>vegastrike-upon-the-coldest-sea</code> &mdash; Vega Strike: Upon the Coldest Sea Assets <em>(also installable as <code>vsutcs</code>)</em></li>
        <li><code>vsu-black-paralysis</code> &mdash; VSU: Black Paralysis Assets <em>(also installable as <code>vsubp</code>)</em></li>
      </ul>
    </div>

    <!-- Nav tabs -->
    <ul class="nav nav-tabs" role="tablist">
      <li role="presentation" class="active"><a href="#fedora" aria-controls="fedora" role="tab" data-toggle="tab">Fedora / RPM</a></li>
      <li role="presentation"><a href="#opensuse" aria-controls="opensuse" role="tab" data-toggle="tab">openSUSE / Zypper</a></li>
      <li role="presentation"><a href="#rocky" aria-controls="rocky" role="tab" data-toggle="tab">Rocky Linux / EL</a></li>
      <li role="presentation"><a href="#debian" aria-controls="debian" role="tab" data-toggle="tab">Debian</a></li>
      <li role="presentation"><a href="#ubuntu" aria-controls="ubuntu" role="tab" data-toggle="tab">Ubuntu / Mint</a></li>
    </ul>

    <!-- Tab panes -->
    <div class="tab-content">
      
      <!-- Fedora Tab -->
      <div role="tabpanel" class="tab-pane active" id="fedora">
        <h3>Fedora (DNF / RPM)</h3>
        
        <h4>1. Add the Repository File</h4>
        <pre class="code-block"><code>sudo dnf config-manager --add-repo https://www.vega-strike.org/repositories/fedora/vegastrike-fedora.repo</code></pre>
        <p><small>Or download: <a href="/repositories/fedora/vegastrike-fedora.repo" download class="site-nav">Download vegastrike-fedora.repo</a></small></p>

        <div class="channel-box channel-stable">
          <h4 class="channel-title" style="color: #56d364;">Stable Channel (Default)</h4>
          <p>Installs the latest official stable release (e.g. 0.9.1):</p>
          <pre class="code-block"><code>sudo dnf install vegastrike vegastrike-upon-the-coldest-sea</code></pre>
          <p><small>Also installable using the alias: <code>sudo dnf install vegastrike vsutcs</code></small></p>
        </div>

        <div class="channel-box channel-testing">
          <h4 class="channel-title" style="color: #e3b341;">Testing Channel (Alphas &amp; Betas: 0.10.x, 0.11.x, Black Paralysis)</h4>
          <p>To install preview builds or Black Paralysis:</p>
          <pre class="code-block"><code># Install Vega Strike Engine &amp; Upon the Coldest Sea
sudo dnf install --enablerepo=vegastrike-testing vegastrike vegastrike-upon-the-coldest-sea

# Install VSU: Black Paralysis
sudo dnf install --enablerepo=vegastrike-testing vegastrike vsu-black-paralysis</code></pre>
          <p><small>To permanently enable testing: <code>sudo dnf config-manager --set-enabled vegastrike-testing</code></small></p>
        </div>
      </div>

      <!-- openSUSE Tab -->
      <div role="tabpanel" class="tab-pane" id="opensuse">
        <h3>openSUSE Leap (Zypper / YaST)</h3>

        <h4>1. Add the Repository</h4>
        <pre class="code-block"><code>sudo zypper addrepo https://www.vega-strike.org/repositories/opensuse/vegastrike-opensuse.repo
sudo zypper refresh</code></pre>

        <div class="channel-box channel-stable">
          <h4 class="channel-title" style="color: #56d364;">Stable Channel (Default)</h4>
          <pre class="code-block"><code>sudo zypper install vegastrike vegastrike-upon-the-coldest-sea</code></pre>
        </div>

        <div class="channel-box channel-testing">
          <h4 class="channel-title" style="color: #e3b341;">Testing Channel (Alphas &amp; Betas: 0.10.x, 0.11.x, Black Paralysis)</h4>
          <pre class="code-block"><code># Install Vega Strike Engine &amp; Upon the Coldest Sea
sudo zypper install --from vegastrike-testing vegastrike vegastrike-upon-the-coldest-sea

# Install VSU: Black Paralysis
sudo zypper install --from vegastrike-testing vegastrike vsu-black-paralysis</code></pre>
        </div>
      </div>

      <!-- Rocky Linux Tab -->
      <div role="tabpanel" class="tab-pane" id="rocky">
        <h3>Rocky Linux / RHEL / CentOS Stream (DNF)</h3>

        <h4>1. Add the Repository</h4>
        <pre class="code-block"><code>sudo dnf config-manager --add-repo https://www.vega-strike.org/repositories/rocky/vegastrike-rocky.repo</code></pre>

        <div class="channel-box channel-stable">
          <h4 class="channel-title" style="color: #56d364;">Stable Channel (Default)</h4>
          <pre class="code-block"><code>sudo dnf install vegastrike vegastrike-upon-the-coldest-sea</code></pre>
        </div>

        <div class="channel-box channel-testing">
          <h4 class="channel-title" style="color: #e3b341;">Testing Channel (Alphas &amp; Betas: 0.10.x, 0.11.x, Black Paralysis)</h4>
          <pre class="code-block"><code># Install Vega Strike Engine &amp; Upon the Coldest Sea
sudo dnf install --enablerepo=vegastrike-testing vegastrike vegastrike-upon-the-coldest-sea

# Install VSU: Black Paralysis
sudo dnf install --enablerepo=vegastrike-testing vegastrike vsu-black-paralysis</code></pre>
        </div>
      </div>

      <!-- Debian Tab -->
      <div role="tabpanel" class="tab-pane" id="debian">
        <h3>Debian (APT)</h3>

        <div class="channel-box channel-stable">
          <h4 class="channel-title" style="color: #56d364;">Stable Channel (Default)</h4>
          <p>Configures the repository for stable releases (component <code>main</code>):</p>
          <pre class="code-block"><code>sudo curl -sSL https://www.vega-strike.org/repositories/debian/vegastrike.sources -o /etc/apt/sources.list.d/vegastrike.sources
sudo apt update
sudo apt install vegastrike vegastrike-upon-the-coldest-sea</code></pre>
        </div>

        <div class="channel-box channel-testing">
          <h4 class="channel-title" style="color: #e3b341;">Testing Channel (Alphas &amp; Betas: 0.10.x, 0.11.x, Black Paralysis)</h4>
          <p>To enable preview testing builds (component <code>testing</code>):</p>
          <pre class="code-block"><code>echo "deb [trusted=yes] https://www.vega-strike.org/repositories/debian $(lsb_release -cs) testing" | sudo tee /etc/apt/sources.list.d/vegastrike-testing.list
sudo apt update

# Install Upon the Coldest Sea or Black Paralysis:
sudo apt install vegastrike vegastrike-upon-the-coldest-sea
sudo apt install vegastrike vsu-black-paralysis</code></pre>
        </div>
      </div>

      <!-- Ubuntu Tab -->
      <div role="tabpanel" class="tab-pane" id="ubuntu">
        <h3>Ubuntu &amp; Linux Mint (APT)</h3>

        <div class="channel-box channel-stable">
          <h4 class="channel-title" style="color: #56d364;">Stable Channel (Default)</h4>
          <pre class="code-block"><code>sudo curl -sSL https://www.vega-strike.org/repositories/ubuntu/vegastrike.sources -o /etc/apt/sources.list.d/vegastrike.sources
sudo apt update
sudo apt install vegastrike vegastrike-upon-the-coldest-sea</code></pre>
        </div>

        <div class="channel-box channel-testing">
          <h4 class="channel-title" style="color: #e3b341;">Testing Channel (Alphas &amp; Betas: 0.10.x, 0.11.x, Black Paralysis)</h4>
          <pre class="code-block"><code>echo "deb [trusted=yes] https://www.vega-strike.org/repositories/ubuntu $(lsb_release -cs) testing" | sudo tee /etc/apt/sources.list.d/vegastrike-testing.list
sudo apt update

# Install Upon the Coldest Sea or Black Paralysis:
sudo apt install vegastrike vegastrike-upon-the-coldest-sea
sudo apt install vegastrike vsu-black-paralysis</code></pre>
        </div>
      </div>

    </div>

    <div style="margin-top: 40px;">
      <h3>Channel &amp; Repository Layout</h3>
      <p style="color: #8b949e;">Each distribution provides separate Stable and Testing repodata:</p>
      <ul>
        <li><strong>Fedora Stable:</strong> <code>/repositories/fedora/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>Fedora Testing:</strong> <code>/repositories/fedora-testing/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>openSUSE Stable:</strong> <code>/repositories/opensuse/leap/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>openSUSE Testing:</strong> <code>/repositories/opensuse-testing/leap/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>Rocky Linux Stable:</strong> <code>/repositories/rocky/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>Rocky Linux Testing:</strong> <code>/repositories/rocky-testing/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><strong>Debian &amp; Ubuntu:</strong> Component <code>main</code> (Stable) and Component <code>testing</code> (Alphas/Betas)</li>
      </ul>
      <p style="color: #8b949e;">All package files stream on demand from official GitHub Release binaries.</p>
    </div>

  </div>

  <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
  <script src="/assets/js/bootstrap.min.js"></script>
  <script>
    // Native robust tab switching support (works offline and alongside Bootstrap)
    document.addEventListener("DOMContentLoaded", function () {{
      var tabLinks = document.querySelectorAll('.nav-tabs a[data-toggle="tab"]');
      tabLinks.forEach(function (link) {{
        link.addEventListener("click", function (e) {{
          e.preventDefault();
          var targetId = this.getAttribute("href");
          if (!targetId || targetId === "#") return;

          var navList = this.closest("ul");
          if (navList) {{
            navList.querySelectorAll("li").forEach(function (li) {{
              li.classList.remove("active");
            }});
          }}
          if (this.parentElement) {{
            this.parentElement.classList.add("active");
          }}

          var tabContent = document.querySelector(".tab-content");
          if (tabContent) {{
            tabContent.querySelectorAll(".tab-pane").forEach(function (pane) {{
              pane.classList.remove("active");
            }});
            var targetPane = document.querySelector(targetId);
            if (targetPane) {{
              targetPane.classList.add("active");
            }}
          }}
        }});
      }});

      // Add copy button functionality to code blocks
      document.querySelectorAll("pre.code-block").forEach(function (block) {{
        var btn = document.createElement("button");
        btn.className = "btn-copy";
        btn.textContent = "Copy";
        btn.addEventListener("click", function () {{
          var code = block.querySelector("code") ? block.querySelector("code").innerText : block.innerText;
          navigator.clipboard.writeText(code.trim()).then(function () {{
            btn.textContent = "Copied!";
            setTimeout(function () {{ btn.textContent = "Copy"; }}, 2000);
          }});
        }});
        block.appendChild(btn);
      }});
    }});
  </script>
</body>
</html>
"""
    with open(os.path.join(REPOS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build_repositories(packages):
    os.makedirs(REPOS_DIR, exist_ok=True)

    # 1. Fedora RPM repositories (Stable & Testing)
    fedora_dir = os.path.join(REPOS_DIR, "fedora")
    fedora_testing_dir = os.path.join(REPOS_DIR, "fedora-testing")
    os.makedirs(fedora_dir, exist_ok=True)
    os.makedirs(fedora_testing_dir, exist_ok=True)

    fedora_repo_content = """[vegastrike]
name=Vega Strike - Fedora $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/fedora/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d

[vegastrike-testing]
name=Vega Strike Testing (Alphas & Betas) - Fedora $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/fedora-testing/$releasever/$basearch/
enabled=0
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(fedora_dir, "vegastrike-fedora.repo"), "w") as f:
        f.write(fedora_repo_content)
    with open(os.path.join(fedora_testing_dir, "vegastrike-fedora.repo"), "w") as f:
        f.write(fedora_repo_content)

    fedora_pkgs = [p for p in packages if p["distro"] == "fedora" and p["pkg_type"] == "rpm"]
    fedora_versions = sorted(list(set(p["distro_version"] for p in fedora_pkgs)))
    for v in fedora_versions:
        stable_v_pkgs = [p for p in fedora_pkgs if p["distro_version"] == v and not p.get("prerelease", False)]
        testing_v_pkgs = [p for p in fedora_pkgs if p["distro_version"] == v and p.get("prerelease", False)]
        if stable_v_pkgs:
            generate_rpm_repodata(os.path.join(fedora_dir, v, "x86_64"), stable_v_pkgs)
        if testing_v_pkgs:
            generate_rpm_repodata(os.path.join(fedora_testing_dir, v, "x86_64"), testing_v_pkgs)

    # 2. openSUSE RPM repositories (Stable & Testing)
    opensuse_dir = os.path.join(REPOS_DIR, "opensuse")
    opensuse_testing_dir = os.path.join(REPOS_DIR, "opensuse-testing")
    os.makedirs(opensuse_dir, exist_ok=True)
    os.makedirs(opensuse_testing_dir, exist_ok=True)

    opensuse_repo_content = """[vegastrike]
name=Vega Strike - openSUSE Leap $releasever
baseurl=https://www.vega-strike.org/repositories/opensuse/leap/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d

[vegastrike-testing]
name=Vega Strike Testing (Alphas & Betas) - openSUSE Leap $releasever
baseurl=https://www.vega-strike.org/repositories/opensuse-testing/leap/$releasever/$basearch/
enabled=0
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(opensuse_dir, "vegastrike-opensuse.repo"), "w") as f:
        f.write(opensuse_repo_content)
    with open(os.path.join(opensuse_testing_dir, "vegastrike-opensuse.repo"), "w") as f:
        f.write(opensuse_repo_content)

    opensuse_pkgs = [p for p in packages if p["distro"] in ("opensuse", "opensuse-leap") and p["pkg_type"] == "rpm"]
    opensuse_versions = sorted(list(set(p["distro_version"] for p in opensuse_pkgs)))
    for v in opensuse_versions:
        stable_v_pkgs = [p for p in opensuse_pkgs if p["distro_version"] == v and not p.get("prerelease", False)]
        testing_v_pkgs = [p for p in opensuse_pkgs if p["distro_version"] == v and p.get("prerelease", False)]
        if stable_v_pkgs:
            generate_rpm_repodata(os.path.join(opensuse_dir, "leap", v, "x86_64"), stable_v_pkgs)
        if testing_v_pkgs:
            generate_rpm_repodata(os.path.join(opensuse_testing_dir, "leap", v, "x86_64"), testing_v_pkgs)

    # 3. Rocky Linux / EL RPM repositories (Stable & Testing)
    rocky_dir = os.path.join(REPOS_DIR, "rocky")
    rocky_testing_dir = os.path.join(REPOS_DIR, "rocky-testing")
    os.makedirs(rocky_dir, exist_ok=True)
    os.makedirs(rocky_testing_dir, exist_ok=True)

    rocky_repo_content = """[vegastrike]
name=Vega Strike - Rocky Linux $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/rocky/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d

[vegastrike-testing]
name=Vega Strike Testing (Alphas & Betas) - Rocky Linux $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/rocky-testing/$releasever/$basearch/
enabled=0
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(rocky_dir, "vegastrike-rocky.repo"), "w") as f:
        f.write(rocky_repo_content)
    with open(os.path.join(rocky_testing_dir, "vegastrike-rocky.repo"), "w") as f:
        f.write(rocky_repo_content)

    rocky_pkgs = [p for p in packages if p["distro"] == "rocky" and p["pkg_type"] == "rpm"]
    rocky_versions = sorted(list(set(p["distro_version"] for p in rocky_pkgs)))
    for v in rocky_versions:
        stable_v_pkgs = [p for p in rocky_pkgs if p["distro_version"] == v and not p.get("prerelease", False)]
        testing_v_pkgs = [p for p in rocky_pkgs if p["distro_version"] == v and p.get("prerelease", False)]
        major = v.split(".")[0]

        if stable_v_pkgs:
            generate_rpm_repodata(os.path.join(rocky_dir, v, "x86_64"), stable_v_pkgs)
            generate_rpm_repodata(os.path.join(rocky_dir, major, "x86_64"), stable_v_pkgs)
        if testing_v_pkgs:
            generate_rpm_repodata(os.path.join(rocky_testing_dir, v, "x86_64"), testing_v_pkgs)
            generate_rpm_repodata(os.path.join(rocky_testing_dir, major, "x86_64"), testing_v_pkgs)

    # 4. Debian APT repositories (Components: main = stable, testing = prerelease)
    debian_dir = os.path.join(REPOS_DIR, "debian")
    os.makedirs(debian_dir, exist_ok=True)

    debian_pkgs = [p for p in packages if (p["distro"] == "debian" or p["distro"] == "debian-like") and p["pkg_type"] == "deb"]
    deb_suites = sorted(list(set(p["distro_version"] for p in debian_pkgs if p["distro_version"] != "all")))
    deb_asset_pkgs = [p for p in debian_pkgs if p["component"] == "assets"]

    debian_sources = f"""Types: deb
URIs: https://www.vega-strike.org/repositories/debian
Suites: {' '.join(deb_suites)}
Components: main
Trusted: yes
"""
    with open(os.path.join(debian_dir, "vegastrike.sources"), "w") as f:
        f.write(debian_sources)

    default_deb_suite = deb_suites[-1] if deb_suites else "trixie"
    debian_list = f"deb [trusted=yes] https://www.vega-strike.org/repositories/debian {default_deb_suite} main\n"
    with open(os.path.join(debian_dir, "vegastrike.list"), "w") as f:
        f.write(debian_list)

    for s in deb_suites:
        stable_s_pkgs = [p for p in debian_pkgs if p["distro_version"] == s and not p.get("prerelease", False)]
        testing_s_pkgs = [p for p in debian_pkgs if p["distro_version"] == s and p.get("prerelease", False)]
        stable_assets = [p for p in deb_asset_pkgs if not p.get("prerelease", False)]
        testing_assets = [p for p in deb_asset_pkgs if p.get("prerelease", False)]

        components_pkgs = {
            "main": stable_s_pkgs + stable_assets,
            "testing": testing_s_pkgs + testing_assets
        }
        generate_deb_repository(debian_dir, s, components_pkgs, "Debian")

    # 5. Ubuntu APT repositories (Components: main = stable, testing = prerelease)
    ubuntu_dir = os.path.join(REPOS_DIR, "ubuntu")
    os.makedirs(ubuntu_dir, exist_ok=True)

    ubuntu_pkgs = [p for p in packages if (p["distro"] in ("ubuntu", "linuxmint") or p["distro"] == "debian-like") and p["pkg_type"] == "deb"]
    ubuntu_suites = sorted(list(set(p["distro_version"] for p in ubuntu_pkgs if p["distro_version"] != "all")))

    ubuntu_sources = f"""Types: deb
URIs: https://www.vega-strike.org/repositories/ubuntu
Suites: {' '.join(ubuntu_suites)}
Components: main
Trusted: yes
"""
    with open(os.path.join(ubuntu_dir, "vegastrike.sources"), "w") as f:
        f.write(ubuntu_sources)

    default_ubuntu_suite = ubuntu_suites[-1] if ubuntu_suites else "noble"
    ubuntu_list = f"deb [trusted=yes] https://www.vega-strike.org/repositories/ubuntu {default_ubuntu_suite} main\n"
    with open(os.path.join(ubuntu_dir, "vegastrike.list"), "w") as f:
        f.write(ubuntu_list)

    for s in ubuntu_suites:
        stable_s_pkgs = [p for p in ubuntu_pkgs if p["distro_version"] == s and not p.get("prerelease", False)]
        testing_s_pkgs = [p for p in ubuntu_pkgs if p["distro_version"] == s and p.get("prerelease", False)]

        components_pkgs = {
            "main": stable_s_pkgs + stable_assets,
            "testing": testing_s_pkgs + testing_assets
        }
        generate_deb_repository(ubuntu_dir, s, components_pkgs, "Ubuntu")

    # 6. Generate landing page
    generate_landing_page(packages)

    print(f"Generated Linux repositories under {REPOS_DIR}")

def main():
    parser = argparse.ArgumentParser(description="Vega Strike Linux Repositories Generator")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh release metadata from GitHub")
    parser.add_argument("--build", action="store_true", help="Generate repository files under repositories/")
    args = parser.parse_args()

    if not args.fetch and not args.build:
        args.fetch = True
        args.build = True

    packages = []
    if args.fetch:
        packages = collect_release_data()
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(packages, f, indent=2)
        print(f"Saved {len(packages)} package references to {DATA_FILE}")
    else:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                packages = json.load(f)
            cache = load_checksums_cache()
            updated = False
            for p in packages:
                if not p.get("sha256") and p.get("download_url") in cache:
                    p["sha256"] = cache[p["download_url"]]
                    updated = True
            if updated:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(packages, f, indent=2)
            print(f"Loaded {len(packages)} package references from {DATA_FILE}")
        else:
            print(f"Data file {DATA_FILE} not found. Please run with --fetch first.", file=sys.stderr)
            sys.exit(1)

    if args.build:
        build_repositories(packages)

if __name__ == "__main__":
    main()
