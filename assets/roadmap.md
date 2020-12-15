---
layout: page
title: Release Roadmap
permalink: /roadmap/
---

To help all understand our release targets, the following outlines what we are aiming for with new release.

At this time this is not a strict road map. That is, we will not reject work from future targets while working on earlier targets unless it blocks our effort on the existing targets. If a future target gets completed earlier then we may update the road map and related milestones to reflect that it will fall under an earlier release.

## Release 0.6.x
[Milestone](https://github.com/vegastrike/Vega-Strike-Engine-Source/milestone/1) | [Project Board](https://github.com/orgs/vegastrike/projects/7)

Theme: Resurrecting Vega Strike - We Can Release!

Minor release, to get things going.

Goals:
- Release Linux and MacOS binaries, to begin receiving feedback from users.
- Release source code that compiles cleanly.

Notes:
- Windows and Mac releases were not achieved for this release and have been pushed back to a future release.

## Release 0.7.x
[Milestone](https://github.com/vegastrike/Vega-Strike-Engine-Source/milestone/2) | [Project Board](https://github.com/orgs/vegastrike/projects/10)

Theme: Removing Code

Goals:
- drop networking support
- remove unnecessary code
- get things under a big better management
- Last official version supporting Python2

Notes:
- If Windows compilation will be fixed/figured out in the near time, a subsequent release from this branch will be made with Windows binaries.
- Big changes and refactorings will be in future releases.
- Python3 support is available but not officially supported.

## Release 0.8.x
[Milestone](https://github.com/vegastrike/Vega-Strike-Engine-Source/milestone/3) | [Project Board](https://github.com/orgs/vegastrike/projects/11)

Theme: Moving from Python 2 to Python 3

Goals:
- Update the Vega Strike Engine to use Python 3

Notes:
- This will need to be paired with a release of our Asset Repositories that have also been upgraded to support Py3.
- This release is highly focused on the move to Python 3. Provided builds will be against Python3; Python2 support will be available via custom builds.

## Release 0.9.x
[Milestone](https://github.com/vegastrike/Vega-Strike-Engine-Source/milestone/5) | [Project Board](https://github.com/orgs/vegastrike/projects/12)

Theme: Updating

Goals:
- Officially split the Vega Strike Assets and the Vega Strike Engine into separate release cycles
- TBD

Notes:
- Python 2 support will be completely removed.
