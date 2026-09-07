# MagicalDreams Resource Packs

This repository contains two Minecraft Java Edition resource packs:

- `Generic RP` — UI, font resources, and shared models
- `Parks RP` — the complete parks resource pack

Both packs target Minecraft 26.2 and declare support for 1.21.1–26.2.

## Editable models

Blockbench source projects live in [`bbmodel-projects`](bbmodel-projects/README.md). The [tintable spotlight beam](bbmodel-projects/spotlight-beam/README.md) is included in both packs as `spotlight:spotlight_beam`. Its runtime RGB tint requires Java 1.21.4+, even though the packs also support older clients. Shared model exports must be updated in both pack folders.

## Make and push changes

1. Pull the latest `main` branch:

   ```sh
   git switch main
   git pull --ff-only
   ```

2. Edit files inside `Generic RP` or `Parks RP`.

3. Review and commit the changes:

   ```sh
   git status
   git diff
   git add "Generic RP" "Parks RP"
   git commit -m "Describe the resource pack changes"
   git push origin main
   ```

Only stage the pack folders that you actually changed.

## Versioning

Each pack keeps its own version in one authoritative file:

| Pack | Version file |
| --- | --- |
| Generic | `GENERIC_VERSION` |
| Parks | `PARKS_VERSION` |

For routine changes, edit and push. A version bump is optional. When appropriate, update only the affected version file using `X.Y.Z`: patch for fixes (`2.0.1`), minor for compatible additions (`2.1.0`), and major for breaking changes (`3.0.0`). Commit that file with the pack changes.

GitHub assigns each workflow run a build number. The build stamps the ZIP's in-game description with both values, for example `Version 2.0.1 · Build 142`. Both packs share the build number but keep independent versions. Build numbers may have gaps, and rerunning the same workflow run keeps its number.

You no longer need to update the version in `pack.mcmeta`. Its checked-in description is used as a template; packaging replaces the `Version X.Y.Z` text while preserving the pack name, colors, compatibility text, and other metadata. The source folders are not modified.

## Download the latest packs

- [Download Generic pack](https://github.com/MagicalDreams/ResourcePack/releases/latest/download/MagicalDreams-Generic-Pack.zip)
- [Download Parks pack](https://github.com/MagicalDreams/ResourcePack/releases/latest/download/MagicalDreams-Parks-Pack.zip)
- [Browse builds and older downloads](https://github.com/MagicalDreams/ResourcePack/releases)

These links become available after the first successful automated release. Download the desired ZIP and place it directly in Minecraft's `resourcepacks` folder. Replace the previous copy and remove any older version-named copies of that same pack to avoid duplicate entries. Enable the pack in Minecraft; reload resources if it is already enabled.

The download filenames stay constant. The version and build number appear inside the pack and in the release notes. Each release retains both ZIPs for rollback.

## Automatic builds and releases

Pushes to `main` that change a pack folder, version file, build script, or this workflow automatically:

1. Validate metadata and version numbers, stamp descriptions, and build/test both ZIPs.
2. Publish one GitHub release named **Build N**, tagged `build-N` at the exact source commit, containing both packs and their version information.
3. Update the latest-download links when this is the newest published build.

Documentation-only or Blockbench-source-only changes do not trigger a release. Export model changes into the pack folders before pushing them for use in game.

To build without a new commit, open **Actions → Build resource packs → Run workflow** and choose `main`. Other branches do not publish releases. A new manual run gets a new build number; rerunning an existing run resumes its unfinished draft or leaves its already-published release intact. Older retries do not replace newer builds at the latest-download links.

Release publication uses GitHub's built-in workflow token with `contents: write`; no personal access token is needed under normal repository settings. Both ZIPs are uploaded to a draft before publication, so incomplete uploads do not replace the last successful release. Releases replace the previous Actions-artifact download process and manual release creation.

## Build locally

With Python 3 installed, run the same builder used by GitHub Actions:

```sh
python3 scripts/build_packs.py
```

The Minecraft-ready ZIPs are written to the ignored `dist/` folder:

- `dist/MagicalDreams-Generic-Pack.zip`
- `dist/MagicalDreams-Parks-Pack.zip`

Local builds display `Build local`. To test a numbered build, use `python3 scripts/build_packs.py --build-number 142`. The script checks metadata parsing, version formatting, ZIP integrity, and root-level packaged metadata. It does not validate every model/texture or replace an in-game compatibility check.

## Troubleshooting

- **No new release:** confirm the commit reached `main` and changed a watched path, or run the workflow manually.
- **Build or publication failed:** open the failed step in Actions. A failed upload may leave a draft; rerun the failed job to resume it.
- **Publication permission error:** check repository/organization token permissions and tag rules for `build-*`.
- **Wrong displayed version:** update the affected `GENERIC_VERSION` or `PARKS_VERSION` file and push. Confirm Minecraft is using the newly downloaded ZIP.
- **Minecraft cannot detect the pack:** use the attached pack ZIP, not GitHub's generated source-code archive.
