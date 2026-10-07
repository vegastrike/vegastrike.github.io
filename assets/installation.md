---
layout: page
title: Install
permalink: /install/
---

In the past Vega Strike has been available on Windows, Mac, and Linux platforms. Moreover, it has generally had a single
package to install the Vega Strike: Upon the Coldest Sea and the Vega Strike Engine.

Below is a listing of installers for each platform.

## Windows

Vega Strike has been split into two main packages:

- [Vega Strike: Upon the Coldest Sea](https://github.com/vegastrike/Assets-Production/releases)
- [Vega Strike Engine](https://github.com/vegastrike/Vega-Strike-Engine-Source/releases)

To install you will need to:

- download the appropriate package from both sites
- install the Vega Strike Engine package
- install the Vega Strike: Upon the Coldest Sea assets package

NOTE: Please make sure to download the same series from both to ensure full compatibility.

### Windows 10

- <https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1_Windows_10.0.17763_AMD64.exe>
- <https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1_Windows_10.0.17763_AMD64.exe>

### Windows 11

- <https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1_Windows_10.0.20348_AMD64.exe>
- <https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1_Windows_10.0.20348_AMD64.exe>

## macOS

Vega Strike has been split into two main packages:

- [Vega Strike: Upon the Coldest Sea](https://github.com/vegastrike/Assets-Production/releases)
- [Vega Strike Engine](https://github.com/vegastrike/Vega-Strike-Engine-Source/releases)

To install you will need to:

- download the appropriate package from both sites
- install the Vega Strike Engine package
- install the Vega Strike: Upon the Coldest Sea assets package

NOTE: Please make sure to download the same series from both to ensure full compatibility.

macOS 13 is the only macOS version for which installers are available for this release, starting with macOS 13.5. (The
installers are named according to the Darwin version.)

- <https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1_macOS_22.6.0_x86_64.dmg>
- <https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1_macOS_22.6.0_x86_64.dmg>

## Linux

Vega Strike has been split into two main packages:

- [Vega Strike: Upon the Coldest Sea](https://github.com/vegastrike/Assets-Production/releases)
- [Vega Strike Engine](https://github.com/vegastrike/Vega-Strike-Engine-Source/releases)

To install you will need to:

- download the appropriate package from both sites
- install the Vega Strike Engine package
- install the Vega Strike: Upon the Coldest Sea assets package

NOTE: Please make sure to download the same series from both to ensure full compatibility.

NOTE 2: For 0.6.x the configuration program is `vssetup`. Starting with 0.7.x the configuration program is
`vegasettings`.
Starting with 0.10.x, the configuration functionality is built into the game itself, as a settings screen accessible by
pressing Alt+C on the keyboard.

The below provides some examples for individual Linux Distributions.

Once installed there should be a `Vega Strike: Upon the Coldest Sea` shortcut available in your Desktop Environment.
Version 0.7.0 also brings a new shortcut for the `Vega Strike Settings` utility.

### Linux: Desktop Environments

Please note that each Desktop Environment also has its own GUI tooling for installing individual packages.
Please make sure to download the appropriate packages for your distribution (see below) and then use the GUI tooling for
your platform and environment if you like. Just be sure to install them in the correct order.

NOTE: The Vega Strike Engine can now support two modes of using OpenGL; unfortunately this is a compile-time choice. The
old OpenGL methods are supported using the LEGACY builds; while the new method uses the GLVND builds. As of the 0.9.x
series, only the GLVND versions have prebuilt installer packages provided.

The remaining Linux instructions will provide command-line oriented instructions.

#### Red Hat/CentOS/Fedora/Rocky Linux

The `dnf` packaging tool provides support for directly installing from a URL.

##### Fedora 41

	# dnf install https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-fedora-41_x86_64.rpm
	# dnf install https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1-fedora-41.rpm

##### Fedora 40

    # dnf install https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-fedora-40_x86_64.rpm
    # dnf install https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1-fedora-40.rpm

##### Rocky Linux 9.5

    # dnf install https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-rocky-9.5_x86_64.rpm
    # dnf install https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1-rocky-9.5.rpm

#### openSUSE Leap 15.6

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
    $ curl -L0 https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-opensuse-leap-15.6_x86_64.rpm
    $ curl -L0 https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1-opensuse-leap-15.6.rpm
    $ sudo zypper install ./Vega-Strike_v0.9.1-GLVND-opensuse-leap-15.6_x86_64.rpm
    $ sudo zypper install ./vsUTCS_v0.9.1-opensuse-leap-15.6.rpm

#### Debian/Ubuntu/Linux Mint

To install using Apt:

NOTE: GUI installers like qapt-deb-installer can be used as well. Just be sure to install in the same order as listed
below.

NOTE 2: The second installer download is the same for all the Debian-based operating systems supported.

##### Ubuntu 24.04 "Noble"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Ubuntu-noble_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Ubuntu-noble_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Ubuntu 22.04 "Jammy"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Ubuntu-jammy_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Ubuntu-jammy_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Debian 12 "Bookworm"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Debian-bookworm_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Debian-bookworm_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Linux Mint 21.3 "Virginia"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Linuxmint-virginia_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Linuxmint-virginia_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Linux Mint 21.2 "Victoria"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Linuxmint-victoria_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Linuxmint-victoria_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Linux Mint 21.1 "Vera"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Linuxmint-vera_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Linuxmint-vera_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

##### Linux Mint 21 "Vanessa"

    $ cd ~/Downloads
	$ mkdir vegastrike && cd vegastrike
	$ curl -LO https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/download/v0.9.1/Vega-Strike_v0.9.1-GLVND-Linuxmint-vanessa_x86_64.deb
	$ curl -LO https://github.com/vegastrike/Assets-Production/releases/download/v0.9.1/vsUTCS_v0.9.1.deb
	$ sudo apt install ./Vega-Strike_v0.9.1-GLVND-Linuxmint-vanessa_x86_64.deb
	$ sudo apt install ./vsUTCS_v0.9.1.deb

#### Arch Linux

Vega Strike has been set up as an [AUR](https://aur.archlinux.org/packages/?O=0&K=vegastrike). There are many tools
available for installing AURs. For example, to install with `yay` do the following:

	# yay -S vegastrike-git

For more information about AURs see
the [Arch User Repository Documentation](https://wiki.archlinux.org/index.php/Arch_User_Repository).
