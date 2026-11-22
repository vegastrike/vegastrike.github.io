#!/usr/bin/env python3
"""
Vega Strike Linux Repositories Generator
-----------------------------------------
Generates compliant, static Linux package repositories for:
  - Fedora (DNF / RPM)
  - openSUSE (Zypper / YaST / RPM)
  - Rocky Linux / RHEL / CentOS (DNF / RPM)
  - Debian & Ubuntu (APT / DEB)

The metadata files point to assets hosted on GitHub Releases,
avoiding the need to store large binaries in the git repository.
"""

import os
import sys
import re
import json
import gzip
import hashlib
import argparse
from datetime import datetime, timezone
import urllib.request
import xml.etree.ElementTree as ET

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(WORKSPACE_DIR, "_data")
REPOS_DIR = os.path.join(WORKSPACE_DIR, "repositories")
DATA_FILE = os.path.join(DATA_DIR, "repositories.json")

VSE_API_URL = "https://api.github.com/repos/vegastrike/Vega-Strike-Engine-Source/releases?per_page=100"
ASSETS_API_URL = "https://api.github.com/repos/vegastrike/Assets-Production/releases?per_page=100"

def fetch_github_releases(url):
    print(f"Fetching releases from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "VegaStrike-Repo-Generator"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching from {url}: {e}", file=sys.stderr)
        return []

def parse_package_asset(asset, release_tag, repo_source):
    filename = asset.get("name", "")
    if not (filename.endswith(".deb") or filename.endswith(".rpm")):
        return None

    size = asset.get("size", 0)
    download_url = asset.get("browser_download_url", "")
    digest = asset.get("digest")
    sha256 = ""
    if digest and digest.startswith("sha256:"):
        sha256 = digest[7:]

    # Engine packages:
    # e.g.: Vega-Strike_v0.11.0-alpha2-GLVND-fedora-43_x86_64.rpm
    #       Vega-Strike_0.8.0-alpha3-543b3fb719000c1bafe7ace3abd42247460d7470-py3-GLVND-Debian-bullseye_x86_64.deb
    m_vse = re.match(
        r"^Vega-Strike_v?([0-9a-zA-Z\.\-]+?)-(?:[0-9a-f]{40}-)?(?:py3-)?(GLVND|LEGACY)-([A-Za-z]+)-([0-9a-zA-Z\.\-]+)_([0-9a-zA-Z_]+)\.(deb|rpm)$",
        filename
    )
    if m_vse:
        ver, opengl, distro_raw, dist_ver_raw, arch, pkg_type = m_vse.groups()
        distro = distro_raw.lower()
        dist_ver = dist_ver_raw.lower()
        if dist_ver.startswith("leap-"):
            dist_ver = dist_ver.replace("leap-", "")

        return {
            "component": "engine",
            "package_name": "vegastrike",
            "display_name": "Vega Strike Engine",
            "version": ver,
            "opengl": opengl,
            "distro": distro,
            "distro_version": dist_ver,
            "arch": "amd64" if arch == "x86_64" and pkg_type == "deb" else arch,
            "pkg_type": pkg_type,
            "filename": filename,
            "size": size,
            "sha256": sha256,
            "download_url": download_url,
            "release_tag": release_tag,
            "repo_source": repo_source
        }

    # Assets packages (RPM):
    # e.g.: vsUTCS_0.10.0-alpha3-fedora-42.rpm
    #       vsUTCS_0.10.0-alpha3-opensuse-leap-16.0.rpm
    #       vsUTCS_v0.9.1-rocky-9.5.rpm
    m_asset_rpm = re.match(
        r"^vsUTCS_v?([0-9a-zA-Z\.\-]+?)-([a-zA-Z\-]+)-([0-9a-zA-Z\.\-]+)\.rpm$",
        filename
    )
    if m_asset_rpm:
        ver, distro_raw, dist_ver_raw = m_asset_rpm.groups()
        distro = distro_raw.lower()
        dist_ver = dist_ver_raw.lower()
        if distro.startswith("opensuse"):
            distro = "opensuse"
            dist_ver = dist_ver.replace("leap-", "")

        return {
            "component": "assets",
            "package_name": "vsutcs",
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
            "repo_source": repo_source
        }

    # Assets packages (DEB):
    # e.g.: vsUTCS_0.10.0-alpha3.deb
    m_asset_deb = re.match(r"^vsUTCS_v?([0-9a-zA-Z\.\-]+?)\.deb$", filename)
    if m_asset_deb:
        ver = m_asset_deb.group(1)
        return {
            "component": "assets",
            "package_name": "vsutcs",
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
            "repo_source": repo_source
        }

    return None

def collect_release_data():
    vse_releases = fetch_github_releases(VSE_API_URL)
    assets_releases = fetch_github_releases(ASSETS_API_URL)

    packages = []
    seen_urls = set()

    for r in vse_releases:
        tag = r.get("tag_name", "")
        for a in r.get("assets", []):
            pkg = parse_package_asset(a, tag, "Vega-Strike-Engine-Source")
            if pkg and pkg["download_url"] not in seen_urls:
                packages.append(pkg)
                seen_urls.add(pkg["download_url"])

    for r in assets_releases:
        tag = r.get("tag_name", "")
        for a in r.get("assets", []):
            pkg = parse_package_asset(a, tag, "Assets-Production")
            if pkg and pkg["download_url"] not in seen_urls:
                packages.append(pkg)
                seen_urls.add(pkg["download_url"])

    return packages

def generate_rpm_repodata(output_dir, packages_list):
    """
    Generates repomd.xml and primary.xml.gz inside output_dir/repodata/
    pointing directly to package URLs on GitHub Releases.
    """
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
        description = (
            "Vega Strike 3D Space Flight Simulator"
            if p["component"] == "engine"
            else "Vega Strike Upon the Coldest Sea Game Data"
        )

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

def generate_deb_repository(output_dir, suite, packages_list, distro_label="Debian"):
    """
    Generates dists/<suite>/Release and dists/<suite>/main/binary-<arch>/Packages[.gz]
    """
    dists_suite_dir = os.path.join(output_dir, "dists", suite)
    os.makedirs(dists_suite_dir, exist_ok=True)

    arch_map = {}
    for p in packages_list:
        arch = p["arch"]
        arch_map.setdefault(arch, []).append(p)

    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    release_files_meta = []

    for arch, arch_pkgs in arch_map.items():
        bin_dir = os.path.join(dists_suite_dir, "main", f"binary-{arch}")
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
                f"Maintainer: Vega Strike Development Team <nabaco@tutamail.com>",
                f"Installed-Size: {installed_size}",
                f"Filename: {p['download_url']}",
                f"Size: {size}",
                f"SHA256: {sha256}",
                f"Section: games",
                f"Priority: optional",
                f"Homepage: https://www.vega-strike.org",
                f"Description: {p['display_name']}",
                f" Vega Strike is an Open Source 3D Action-Space-Sim that lets you trade,",
                f" fight, and explore in a vast universe."
            ]
            pkg_entries.append("\n".join(entry))

        packages_content = ("\n\n".join(pkg_entries) + "\n").encode("utf-8")

        pkgs_path = os.path.join(bin_dir, "Packages")
        with open(pkgs_path, "wb") as f_pkg:
            f_pkg.write(packages_content)

        pkgs_gz_path = os.path.join(bin_dir, "Packages.gz")
        with gzip.open(pkgs_gz_path, "wb") as f_gz:
            f_gz.write(packages_content)

        rel_pkgs_path = f"main/binary-{arch}/Packages"
        rel_pkgs_gz_path = f"main/binary-{arch}/Packages.gz"

        with open(pkgs_gz_path, "rb") as f_gz_read:
            gz_bytes = f_gz_read.read()

        release_files_meta.append((rel_pkgs_path, len(packages_content), hashlib.md5(packages_content).hexdigest(), hashlib.sha256(packages_content).hexdigest()))
        release_files_meta.append((rel_pkgs_gz_path, len(gz_bytes), hashlib.md5(gz_bytes).hexdigest(), hashlib.sha256(gz_bytes).hexdigest()))

    release_lines = [
        f"Origin: Vega Strike",
        f"Label: Vega Strike {distro_label} Repository",
        f"Suite: {suite}",
        f"Codename: {suite}",
        f"Components: main",
        f"Architectures: {' '.join(sorted(arch_map.keys()))}",
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
    for Fedora, openSUSE, Rocky, Debian, and Ubuntu.
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
    .repo-card:hover {{
      border-color: #4a576d;
    }}
    .distro-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }}
    .badge-fedora {{ background: #294172; color: #fff; }}
    .badge-opensuse {{ background: #173f35; color: #73c48f; }}
    .badge-rocky {{ background: #13382c; color: #10b981; }}
    .badge-debian {{ background: #4a1525; color: #ff6b8b; }}
    .badge-ubuntu {{ background: #4a2612; color: #ff9854; }}
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
    a.site-nav {{
      color: #58a6ff;
      text-decoration: none;
    }}
    a.site-nav:hover {{
      text-decoration: underline;
    }}
    table.table-pkgs {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
      font-size: 0.9em;
    }}
    table.table-pkgs th, table.table-pkgs td {{
      padding: 8px 12px;
      border-bottom: 1px solid #272d38;
    }}
    table.table-pkgs th {{
      color: #8b949e;
      text-align: left;
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
      <strong>Note:</strong> Vega Strike is packaged into two components: the <strong>Engine</strong> (<code>vegastrike</code>) and the <strong>Game Assets</strong> (<code>vsutcs</code>). Both are available through these repositories.
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
        <p>Supports Fedora 40, 41, 42, 43, and 44 (x86_64).</p>
        
        <h4>1. Add the Repository</h4>
        <pre class="code-block"><code>sudo dnf config-manager --add-repo https://www.vega-strike.org/repositories/fedora/vegastrike-fedora.repo</code></pre>
        <p><small>Or download the repo file manually to <code>/etc/yum.repos.d/vegastrike-fedora.repo</code>: <a href="/repositories/fedora/vegastrike-fedora.repo" download class="site-nav">Download vegastrike-fedora.repo</a></small></p>

        <h4>2. Install Vega Strike</h4>
        <pre class="code-block"><code>sudo dnf install vegastrike vsutcs</code></pre>
      </div>

      <!-- openSUSE Tab -->
      <div role="tabpanel" class="tab-pane" id="opensuse">
        <h3>openSUSE Leap (Zypper / YaST)</h3>
        <p>Supports openSUSE Leap 15.6 and Leap 16.0 (x86_64).</p>

        <h4>1. Add the Repository</h4>
        <pre class="code-block"><code>sudo zypper addrepo https://www.vega-strike.org/repositories/opensuse/vegastrike-opensuse.repo
sudo zypper refresh</code></pre>
        <p><small>Or download the repo file manually to <code>/etc/zypp/repos.d/vegastrike-opensuse.repo</code>: <a href="/repositories/opensuse/vegastrike-opensuse.repo" download class="site-nav">Download vegastrike-opensuse.repo</a></small></p>

        <h4>2. Install Vega Strike</h4>
        <pre class="code-block"><code>sudo zypper install vegastrike vsutcs</code></pre>
      </div>

      <!-- Rocky Linux Tab -->
      <div role="tabpanel" class="tab-pane" id="rocky">
        <h3>Rocky Linux / RHEL / CentOS Stream (DNF)</h3>
        <p>Supports Rocky Linux 8, 9, and 10 (x86_64).</p>

        <h4>1. Add the Repository</h4>
        <pre class="code-block"><code>sudo dnf config-manager --add-repo https://www.vega-strike.org/repositories/rocky/vegastrike-rocky.repo</code></pre>
        <p><small>Or download: <a href="/repositories/rocky/vegastrike-rocky.repo" download class="site-nav">Download vegastrike-rocky.repo</a></small></p>

        <h4>2. Install Vega Strike</h4>
        <pre class="code-block"><code>sudo dnf install vegastrike vsutcs</code></pre>
      </div>

      <!-- Debian Tab -->
      <div role="tabpanel" class="tab-pane" id="debian">
        <h3>Debian (APT)</h3>
        <p>Supports Debian Bookworm (12) and Trixie (13) (amd64).</p>

        <h4>1. Configure the Repository</h4>
        <p>Using the modern deb822 sources format (recommended):</p>
        <pre class="code-block"><code>sudo curl -sSL https://www.vega-strike.org/repositories/debian/vegastrike.sources -o /etc/apt/sources.list.d/vegastrike.sources
sudo apt update</code></pre>

        <p>Or traditional <code>sources.list.d</code> entry:</p>
        <pre class="code-block"><code>echo "deb [trusted=yes] https://www.vega-strike.org/repositories/debian $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/vegastrike.list
sudo apt update</code></pre>

        <h4>2. Install Vega Strike</h4>
        <pre class="code-block"><code>sudo apt install vegastrike vsutcs</code></pre>
        <p><small>Direct release downloads are also accessible at <a href="https://github.com/vegastrike/Vega-Strike-Engine-Source/releases" target="_blank" class="site-nav">Vega Strike Engine Releases</a>.</small></p>
      </div>

      <!-- Ubuntu Tab -->
      <div role="tabpanel" class="tab-pane" id="ubuntu">
        <h3>Ubuntu &amp; Linux Mint (APT)</h3>
        <p>Supports Ubuntu 22.04 LTS (Jammy), 24.04 LTS (Noble), 26.04 (Resolute), and Linux Mint.</p>

        <h4>1. Configure the Repository</h4>
        <pre class="code-block"><code>sudo curl -sSL https://www.vega-strike.org/repositories/ubuntu/vegastrike.sources -o /etc/apt/sources.list.d/vegastrike.sources
sudo apt update</code></pre>

        <p>Or traditional <code>sources.list.d</code> entry:</p>
        <pre class="code-block"><code>echo "deb [trusted=yes] https://www.vega-strike.org/repositories/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/vegastrike.list
sudo apt update</code></pre>

        <h4>2. Install Vega Strike</h4>
        <pre class="code-block"><code>sudo apt install vegastrike vsutcs</code></pre>
      </div>

    </div>

    <div style="margin-top: 40px;">
      <h3>Repository Structure Overview</h3>
      <p style="color: #8b949e;">Each repository conforms to the native package manager specifications:</p>
      <ul>
        <li><code>/repositories/fedora/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><code>/repositories/opensuse/leap/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><code>/repositories/rocky/$releasever/$basearch/repodata/repomd.xml</code></li>
        <li><code>/repositories/debian/dists/$suite/main/binary-amd64/Packages.gz</code></li>
        <li><code>/repositories/ubuntu/dists/$suite/main/binary-amd64/Packages.gz</code></li>
      </ul>
      <p style="color: #8b949e;">Packages are streamed on demand directly from official GitHub Release binaries.</p>
    </div>

  </div>

  <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
  <script src="/assets/js/bootstrap.min.js"></script>
  <script>
    // Native robust tab switching support (works offline and alongside Bootstrap)
    document.addEventListener("DOMContentLoaded", function () {
      var tabLinks = document.querySelectorAll('.nav-tabs a[data-toggle="tab"]');
      tabLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
          e.preventDefault();
          var targetId = this.getAttribute("href");
          if (!targetId || targetId === "#") return;

          var navList = this.closest("ul");
          if (navList) {
            navList.querySelectorAll("li").forEach(function (li) {
              li.classList.remove("active");
            });
          }
          if (this.parentElement) {
            this.parentElement.classList.add("active");
          }

          var tabContent = document.querySelector(".tab-content");
          if (tabContent) {
            tabContent.querySelectorAll(".tab-pane").forEach(function (pane) {
              pane.classList.remove("active");
            });
            var targetPane = document.querySelector(targetId);
            if (targetPane) {
              targetPane.classList.add("active");
            }
          }
        });
      });

      // Add copy button functionality to code blocks
      document.querySelectorAll("pre.code-block").forEach(function (block) {
        var btn = document.createElement("button");
        btn.className = "btn-copy";
        btn.textContent = "Copy";
        btn.addEventListener("click", function () {
          var code = block.querySelector("code") ? block.querySelector("code").innerText : block.innerText;
          navigator.clipboard.writeText(code.trim()).then(function () {
            btn.textContent = "Copied!";
            setTimeout(function () { btn.textContent = "Copy"; }, 2000);
          });
        });
        block.appendChild(btn);
      });
    });
  </script>
</body>
</html>
"""
    with open(os.path.join(REPOS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build_repositories(packages):
    os.makedirs(REPOS_DIR, exist_ok=True)

    # 1. Fedora RPM repositories
    # Distro versions: 40, 41, 42, 43, 44
    fedora_dir = os.path.join(REPOS_DIR, "fedora")
    os.makedirs(fedora_dir, exist_ok=True)

    fedora_repo_content = """[vegastrike-fedora]
name=Vega Strike - Fedora $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/fedora/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(fedora_dir, "vegastrike-fedora.repo"), "w") as f:
        f.write(fedora_repo_content)

    fedora_pkgs = [p for p in packages if p["distro"] == "fedora" and p["pkg_type"] == "rpm"]
    fedora_versions = sorted(list(set(p["distro_version"] for p in fedora_pkgs)))
    for v in fedora_versions:
        v_pkgs = [p for p in fedora_pkgs if p["distro_version"] == v]
        v_dir = os.path.join(fedora_dir, v, "x86_64")
        generate_rpm_repodata(v_dir, v_pkgs)

    # 2. openSUSE RPM repositories
    opensuse_dir = os.path.join(REPOS_DIR, "opensuse")
    os.makedirs(opensuse_dir, exist_ok=True)

    opensuse_repo_content = """[vegastrike-opensuse]
name=Vega Strike - openSUSE Leap $releasever
baseurl=https://www.vega-strike.org/repositories/opensuse/leap/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(opensuse_dir, "vegastrike-opensuse.repo"), "w") as f:
        f.write(opensuse_repo_content)

    opensuse_pkgs = [p for p in packages if p["distro"] in ("opensuse", "opensuse-leap") and p["pkg_type"] == "rpm"]
    opensuse_versions = sorted(list(set(p["distro_version"] for p in opensuse_pkgs)))
    for v in opensuse_versions:
        v_pkgs = [p for p in opensuse_pkgs if p["distro_version"] == v]
        v_dir = os.path.join(opensuse_dir, "leap", v, "x86_64")
        generate_rpm_repodata(v_dir, v_pkgs)

    # 3. Rocky Linux / EL RPM repositories
    rocky_dir = os.path.join(REPOS_DIR, "rocky")
    os.makedirs(rocky_dir, exist_ok=True)

    rocky_repo_content = """[vegastrike-rocky]
name=Vega Strike - Rocky Linux $releasever - $basearch
baseurl=https://www.vega-strike.org/repositories/rocky/$releasever/$basearch/
enabled=1
gpgcheck=0
repo_gpgcheck=0
metadata_expire=1d
"""
    with open(os.path.join(rocky_dir, "vegastrike-rocky.repo"), "w") as f:
        f.write(rocky_repo_content)

    rocky_pkgs = [p for p in packages if p["distro"] == "rocky" and p["pkg_type"] == "rpm"]
    rocky_versions = sorted(list(set(p["distro_version"] for p in rocky_pkgs)))
    for v in rocky_versions:
        v_pkgs = [p for p in rocky_pkgs if p["distro_version"] == v]
        v_dir = os.path.join(rocky_dir, v, "x86_64")
        generate_rpm_repodata(v_dir, v_pkgs)

        # Also support major release (e.g. 9 for 9.8, 10 for 10.2, 8 for 8.5)
        major = v.split(".")[0]
        major_dir = os.path.join(rocky_dir, major, "x86_64")
        generate_rpm_repodata(major_dir, v_pkgs)

    # 4. Debian APT repositories
    debian_dir = os.path.join(REPOS_DIR, "debian")
    os.makedirs(debian_dir, exist_ok=True)

    debian_sources = """Types: deb
URIs: https://www.vega-strike.org/repositories/debian
Suites: bookworm trixie
Components: main
Trusted: yes
"""
    with open(os.path.join(debian_dir, "vegastrike.sources"), "w") as f:
        f.write(debian_sources)

    debian_list = "deb [trusted=yes] https://www.vega-strike.org/repositories/debian bookworm main\n"
    with open(os.path.join(debian_dir, "vegastrike.list"), "w") as f:
        f.write(debian_list)

    debian_pkgs = [p for p in packages if (p["distro"] == "debian" or p["distro"] == "debian-like") and p["pkg_type"] == "deb"]
    # Group by suites
    deb_suites = ["bookworm", "trixie"]
    deb_asset_pkgs = [p for p in debian_pkgs if p["component"] == "assets"]

    for s in deb_suites:
        s_pkgs = [p for p in debian_pkgs if p["distro_version"] == s] + deb_asset_pkgs
        if s_pkgs:
            generate_deb_repository(debian_dir, s, s_pkgs, "Debian")

    # 5. Ubuntu APT repositories
    ubuntu_dir = os.path.join(REPOS_DIR, "ubuntu")
    os.makedirs(ubuntu_dir, exist_ok=True)

    ubuntu_sources = """Types: deb
URIs: https://www.vega-strike.org/repositories/ubuntu
Suites: jammy noble resolute
Components: main
Trusted: yes
"""
    with open(os.path.join(ubuntu_dir, "vegastrike.sources"), "w") as f:
        f.write(ubuntu_sources)

    ubuntu_list = "deb [trusted=yes] https://www.vega-strike.org/repositories/ubuntu noble main\n"
    with open(os.path.join(ubuntu_dir, "vegastrike.list"), "w") as f:
        f.write(ubuntu_list)

    ubuntu_pkgs = [p for p in packages if (p["distro"] in ("ubuntu", "linuxmint") or p["distro"] == "debian-like") and p["pkg_type"] == "deb"]
    ubuntu_suites = ["jammy", "noble", "resolute"]
    for s in ubuntu_suites:
        s_pkgs = [p for p in ubuntu_pkgs if p["distro_version"] == s] + deb_asset_pkgs
        if s_pkgs:
            generate_deb_repository(ubuntu_dir, s, s_pkgs, "Ubuntu")

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
            print(f"Loaded {len(packages)} package references from {DATA_FILE}")
        else:
            print(f"Data file {DATA_FILE} not found. Please run with --fetch first.", file=sys.stderr)
            sys.exit(1)

    if args.build:
        build_repositories(packages)

if __name__ == "__main__":
    main()
