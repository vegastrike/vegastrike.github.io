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

### Linux: Red Hat/CentOS/Fedora

The `dnf` packaging tool provides support for directly installing from a URL:

	```
	# dnf install https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.6.0/vega-strike_v0.6.0-centos-8.rpm
	# dnf install https://github.com/vegastrike/Assets-Production/releases/download/v0.6.2/vsUTCS_v0.6.2-centos-8.rpm
	```

NOTE: This doesn't work yet as we missed getting the RPMs build for the Vega Strike Engine 0.6.0 Release. See [here for details](https://github.com/vegastrike/Vega-Strike-Engine-Source/issues/368)

### Linux: Debian/Ubuntu

To install using Apt:

	```
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.6.0/vega-strike_v0.6.0-Ubuntu-xenial_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.6.2/vsUTCS_v0.6.2.deb
	$ sudo dpkg -i vega-strike_v0.6.0-Ubuntu-xenial_x86_64.deb
	$ sudo dpkg -i vsUTCS_v0.6.2.deb
	```
### Linux: Arch

To install using an AUR:

	```
	TBD
	```
