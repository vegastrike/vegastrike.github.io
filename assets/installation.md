---
layout: page
title: Install
permalink: /install/
---

In the past Vega Strike has been available on Windows, Mac, and Linux platforms. Moreover it has generally had a single package to install the Vega Strike: Upon the Coldest Sea and the Vega Strike Engine.

Below is a listing of installation for each platform.

## Windows

We have not yet restored building the latest versions for Windows.
Please see the [Vega Strike 0.5.1](https://sourceforge.net/projects/vegastrike/files/vegastrike/0.5.1/) for a release to use.

## Mac OS X

We have not yet restored building the latest versions for Mac OS X.
Please see the [Vega Strike 0.5.0](https://sourceforge.net/projects/vegastrike/files/vegastrike/0.5.0/) for a release to use.

## Linux

Vega Strike has been split into two main packages:
- [Vega Strike: Upon the Coldest Sea](https://github.com/vegastrike/Assets-Production/releases)
- [Vega Strike Engine](https://github.com/vegastrike/Vega-Strike-Engine-Source/releases)

To install you will need to:
- download the appropriate package from both sites 
- install the Vega Strike Engine package
- install the Vega Strike: Upon the Coldest Sea assets package

NOTE: For versions 0.6.x through 0.8.x please make sure to download the same series from both to ensure full compatibility.
NOTE: For 0.6.x the configuration program is `vssetup`. Starting with 0.7.x the configuration program will be `vegasettings`.

The below provides some examples for individual Linux Distributions.

Once installed there should be a `Vega Strike: Upon the Coldest Sea` shortcut available in your Desktop Environment.
Version 0.7.0 also brings a new short cut for the `vega Strike Settings` utility.

### Linux: Desktop Environments

Please note that each Desktop Environment also has its own GUI tooling for installing individual packages.
Please make sure to download the appropriate packages for your distribution (see below) and then use the GUI tooling for your
platform and environment if you like. Just be sure to install them in the correct order.

The remaining Linux instructions will provide command-line oriented instructions.

### Linux: Red Hat/CentOS/Fedora

The `dnf` packaging tool provides support for directly installing from a URL:

	# dnf install https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.7.0/Vega-Strike_v0.7.0-py3-centos-8_x86_64.rpm
	# dnf install https://github.com/vegastrike/Assets-Production/releases/download/v0.7.0/vsUTCS_v0.7.0-centos-8.rpm

### Linux: Debian/Ubuntu

To install using Apt:

	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.7.0/Vega-Strike_v0.7.0-py2-Ubuntu-xenial_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.7.0/vsUTCS_v0.7.0.deb
	$ sudo apt install ./Vega-Strike_v0.7.0-py2-Ubuntu-xenial_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.7.0.deb

NOTE: GUI installers like qapt-deb-installer can be used as well. Just be sure to install in the same order as listed above.

### Linux: Arch

Vega Strike has been setup as an [AUR](https://aur.archlinux.org/packages/?O=0&K=vegastrike). There are many tools available for installing AURs. For example, to install with `yay` do the following:

	# yay -S vegastrike-git

For more information about AURs see the [Arch User Repository Documentation](https://wiki.archlinux.org/index.php/Arch_User_Repository).
