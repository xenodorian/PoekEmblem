# For New Agents (read this first)

Written by a Grok session that started from scratch. It lists what cost time so you can skip it.

## Which repo is which
- PoekEmblem (this repo): Fire Emblem x FireRed hack. Eirika replaces Leaf. This is the project. Start with Current_Work.md, then PROGRESS_LOG.txt.
- Pokemon-War-and-Murder: the unrelated Pokemon Outlaw hack. Ignore its story steps (Max, Viridian arrest, soldiers) unless the owner says otherwise.
- FE8: partial mirror of the Fire Emblem 8 decomp (89 files). fireemblem8u (upstream) is the full tree.
- Other repos (CryMon, SGBA, GitROMs) are unrelated to this hack.

## Where things are
- Built ROMs: builds/ (never overwrite; use new filenames). Test hook ROMs: builds/test/.
- IPS patches: patches/.
- Full working decomp tree: decomp_full.tar.gz (unpack, copy, then make -j8). decomp_overlay/ is only the changed files over pret/pokefirered commit 037335f.
- Test harness: workdata/harness/ (shot, shot_save, watch; need libmgba0.10). Saves: workdata/saves/.
- FE8 art is derived from the FE8 ROM in the repo root; art scripts are in tools/.

## Hard rules from the owner
- Never delete, overwrite, or move ROMs, IPS patches, saves, states, or art. Work on copies.
- No em dashes, no emoji. Short factual reports.
- Build features. Do not spend sessions only testing. After each large step update Current_Work.md, commit, and push.
- Confirm before edits that are unclear or out of scope.

## Access and tools
- The GitHub MCP connector only writes text files. For binaries use git over https with the gh CLI: gh auth login -h github.com -p https -s repo,workflow -w, then gh auth setup-git. The owner enters the device code in a browser.
- gh may already be logged in on the box: check gh auth status first.
- Installed on the box already: arm-none-eabi toolchain, agbcc, libpng, python3. mGBA is not installed by default.
- The box is shared by all agents. Other agents may be editing the same folders. Check git status and git fetch before working, and use a fresh clone if a folder is changing under you.

## Mistakes that wasted time
- Stale local clone: always git fetch and pull before saying a file is missing. Do not report "not in the repo" without checking git log --all and the GitHub web state.
- Reading only one repo, or only for ROMs, and concluding nothing was uploaded.
- Running make on the overlay alone: it fails (missing graphics). Use decomp_full.tar.gz.
- Assuming the Outlaw notes apply here. They do not.

## Known state
See Current_Work.md. Chapters 4, 12 and 16-22 stalled in one test only because the test Eirika had Normal moves vs Ghost enemies; that is a test setup issue.
