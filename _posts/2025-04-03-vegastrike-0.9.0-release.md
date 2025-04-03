---
layout: post
title: "Vega Strike 0.9.0 Released!"
description: "New Releases: Vega Strike 0.9.0, VS:UtCS 0.9.0"
author: BenjamenMeyer
date: 2025-04-03 00:00:00 +0000
categories: website announcements releases community
excerpt_separator: <!--more-->
---
It is with great pleasure that the Vega Strike Development Team announces the release of Vega Strike 0.9.0 and VS:Upon The Coldest Sea 0.9.0.
<!--more-->

Join our protagonist Deucalion in adventures around the universe as a bounty hunter, mercenary, or merchant flying through the
stars. Meet the deadly Aera and mysterious Rlaan. Battle with the Confederation. Run alongside Pirates. Or just buy and sell as a merchant while you
explore. The universe and adventure are yours.

## What's changed?

Since our last release in March 2022 of Vega Strike 0.8.0 we've continued to refactor the code and make general improvements.

While we have continued to refactor, make improvements, fix bugs, and update dependencies much of the 0.9.0 release was
focused around restoring support for Mac and Windows. It is therefore with great pleasure that the Vega Strike Development
Team is pleased to announce that we have been able to not only restore providing builds for all three of our major platforms
(Linux, Mac, and Windows) but we have also been able to provide installers for Mac and Windows. A great thanks goes out
to Stephen G. Tuggy and others that have contributed and tested on these platforms to help make this great achievement
possible.

As noted with the 0.8.0 release we have completely dropped support for Python2 and are 100% Python3 oriented. We have also
dropped providing builds with the LEGACY OpenGL support; however, support remains in the source code should anyone still
need it.

As part of updating the Vega Strike Engine we have started a journey to update how we store and load data. With the 0.9.0
release we have moved our a number of our data assets from defaulting to using a CSV format to now using a JSON format.
While the format is not as nice to use in tools like LibreOffice Calc or Microsoft Excel, this will help reduce errors and
make it easier to maintain the files.

Finally, our Vega Strike Engine API has been updated to Engine API 2 which moves some functionality to the Game Assets in
addition to the CSV to JSON file format changes.

As a reminder, the Vega Strike Engine application is available as `vegastrike-engine` which requires the `-D` parameter to specify
where to find the Game Assets. The `vegastrike` binary is still being provided at this time and it will continue to autofind
the assets like with previous versions. However, we strongly advise moving to the new `vegastrike-engine` binary and specifying
the parameter for the Game Assets as we will be dropping the old binary name (vegastrike) in a future release.

For a complete list of differences see [Vega Strike Engine Delta][vsedelta] and [Vega Strike: Upon the Coldest Sea Delta][vsutcsdelta].

## Want to help out?

There's a lot to do. We're working diligently to update Vega Strike. Version 0.10.0 is our next step along the line which will be
continuing to bring big improvements to the engine. We've already got several releases planned in the process of continuing to update
our dependencies and fix bugs; you can see our [Road Map][roadmap]. We need everything from coding, story development, art work,
documentation, and even just generally helping the community.

The development team is active at [Gitter.im][gitter] and we'd love to hear from you.

You can also find the community at the [Vega Strike Forums][forums].

## Where can I find the release?

[Vega Strike Engine 0.9.0][vse]
[Vega Strike: Upon the Coldest Sea 0.9.0][vsutcs]

[gh]: https://github.com/vegastrike
[roadmap]: https://www.vega-strike.org/roadmap/
[gitter]: https://gitter.im/vegastrike/community
[forums]: https://forums.vega-strike.org/
[vse]: https://github.com/vegastrike/Vega-Strike-Engine-Source/releases/tag/v0.9.0
[vsutcs]: https://github.com/vegastrike/Assets-Production/releases/tag/v0.9.0
[vsedelta]: https://github.com/vegastrike/Vega-Strike-Engine-Source/compare/v0.8.0...v0.9.0
[vsutcsdelta]: https://github.com/vegastrike/Assets-Production/compare/v0.8.0...v0.9.0
