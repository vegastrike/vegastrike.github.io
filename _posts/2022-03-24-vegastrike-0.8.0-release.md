---
layout: post
title: "Vega Strike 0.8.0 Released!"
description: "New Releases: Vega Strike 0.8.0, VS:UtCS 0.8.0"
author: BenjamenMeyer
date: 2022-03-24 00:00:00 +0000
categories: website announcements releases community
excerpt_separator: <!--more-->
---
It is with great pleasure that the Vega Strike Development Team announces the release of Vega Strike 0.8.0 and VS:Upon The Coldest Sea 0.8.0.
<!--more-->

Join our protagonist Deucalion in adventures around the universe as a bounty hunter, mercenary, or merchant flying through the
stars. Meet the deadly Aera and mysterious Rlaan. Battle with the Confederation. Run alongside Pirates. Or just buy and sell as a merchant while you
explore. The universe and adventure are yours.

## What's changed?

Since our last release last April of Vega Strike 0.7.0 we've continued to refactor the code and make general improvements.

We have also made the Python3 Support the official build. We are no longer providing Python2 builds; if you need Python2 it is still
available but you must make your own build from source. Python2 support will be completely removed in our next release (0.9.0).

Some changes to OpenGL have also required that we provide two separate builds on Linux Platforms. Unfortunately this requires making
separate builds due to linking against libraries that we can't do otherwise. Our old methods of using OpenGL are available using the
"LEGACY" builds; while the newer support is provided using the "GLVND" builds.

The Vega Strike Engine now supports a Versioning API that provides the release version (e.g 0.8.0) and the Engine API Version (e.g 1).
The Engine API version works much like the Android API Version - it's a simple incrementing unsigned integer value. If the API does
not exist (import error in Python) then the Engine API Version is zero (0) and the release version is at most 0.7.0, but can also
be any earlier version. We highly recommend that game assets developers gate on this API as going forward we are going to start
introducing changes where games will need to rely on the Engine API Version value to determine that they are compatible with the
engine. Aside from the introduction of this API there is no difference in the Python API provided from 0.7.0.

The Vega Strike Developers are also putting in place a standard binary naming convension of `vegastrike-<tool` or `libvegastrike-<library>`.
This is to help associate all our tools and libraries. Binaries using the new naming convension will also not be specific to any given
game asset and will require the appropriate parameter to specify where to find the game assets when applicable.

With 0.8.x we have restored the ability to build on the Mac and Windows platforms. However we're not quite ready to provide pre-built
binaries. Please watch our next release for pre-built binaries. In the meantime we invite you to download the source and build! If you
still need a pre-built binary and don't mind an old version then please visit our old [SourceForge site][sf] to find the 0.5.x releases.

NOTE: Under Windows the Vega Strike Settings utility is currently broken due to a dependency being flagged by Windows improperly and
therefore preventing the utility from being able to run. Fixing this will be a priority for releasing 0.9.x.

For a complete list of differences see [Vega Strike Engine Delta][vsedelta] and [Vega Strike: Upon the Coldest Sea Delta][vsutcsdelta].

## Want to help out?

There's a lot to do. We're working diligently to update Vega Strike. Version 0.9.0 is our next step along the line and will completely
remove Python 2 support.  We've already got several releases planned in the process of continuing to update our dependencies and fix bugs;
you can see our [Road Map][roadmap]. We need everything from coding, story development, art work, documentation, and even just generally helping the community.

The development team is active at [Gitter.im][gitter] and we'd love to hear from you.

You can also find the community at the [Vega Strike Forums][forums].

## Where can I find the release?

[Vega Strike Engine 0.8.0][vse]
[Vega Strike: Upon the Coldest Sea 0.8.0][vsutcs]

NOTE: Presently just the Linux builds are provided. The Vega Strike Team is still working to restore Mac and Windows support.

[sf]: https://sourceforge.net/projects/vegastrike/
[gh]: https://github.com/vegastrike
[roadmap]: https://www.vega-strike.org/roadmap/
[gitter]: https://gitter.im/vegastrike/community
[forums]: https://forums.vega-strike.org/
[vse]: https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/tag/v0.8.0
[vsutcs]: https://github.com/vegastrike/Assets-Production/releases/tag/v0.8.0
[vsedelta]: https://github.com/vegastrike/Vega-Strike-Engine-Source/compare/v0.7.0...v0.8.0
[vsutcsdelta]: https://github.com/vegastrike/Assets-Production/compare/v0.7.1...v0.8.0
