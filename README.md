# MagicalDreams Resource Packs

This repository contains two Minecraft Java Edition resource packs:

- `Generic RP` — UI and font resources
- `Parks RP` — the complete parks resource pack

Both packs target Minecraft 26.2 and declare support for 1.21.1–26.2.

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

## Change a pack version

Each pack has an independent version:

| Pack | Build version | In-game description |
| --- | --- | --- |
| Generic | `GENERIC_VERSION` | `Generic RP/pack.mcmeta` |
| Parks | `PARKS_VERSION` | `Parks RP/pack.mcmeta` |

To release a new version of one pack:

1. Update its version file, for example to `2.1.0`.
2. Update the displayed version in that pack's `pack.mcmeta` description.
3. Commit the version together with the pack changes:

   ```sh
   git add GENERIC_VERSION "Generic RP"
   git commit -m "Release Generic pack 2.1.0"
   git push origin main
   ```

For a Parks release, use `PARKS_VERSION` and `Parks RP` instead.

Use patch versions for fixes (`2.0.1`), minor versions for compatible additions (`2.1.0`), and major versions for breaking changes (`3.0.0`).

## Validate locally

Check the metadata JSON:

```sh
jq empty "Generic RP/pack.mcmeta" "Parks RP/pack.mcmeta"
```

Build the same versioned ZIPs produced by GitHub Actions:

```sh
generic_version=$(<GENERIC_VERSION)
parks_version=$(<PARKS_VERSION)
mkdir -p dist
rm -f "dist/MagicalDreams-Generic-Pack-v${generic_version}.zip" \
      "dist/MagicalDreams-Parks-Pack-v${parks_version}.zip"
(cd "Generic RP" && zip -r "../dist/MagicalDreams-Generic-Pack-v${generic_version}.zip" . -x '*.DS_Store')
(cd "Parks RP" && zip -r "../dist/MagicalDreams-Parks-Pack-v${parks_version}.zip" . -x '*.DS_Store')
unzip -t "dist/MagicalDreams-Generic-Pack-v${generic_version}.zip"
unzip -t "dist/MagicalDreams-Parks-Pack-v${parks_version}.zip"
```

Each ZIP must contain `pack.mcmeta` at its root, not inside another folder.

## Get a new build from GitHub Actions

Every push to `main` automatically runs **Build resource packs**.

1. Open the repository's **Actions** tab.
2. Select **Build resource packs**.
3. Open the latest successful run.
4. Download the versioned Generic or Parks ZIP under **Artifacts**.
5. Put that downloaded ZIP directly in Minecraft's `resourcepacks` folder.

To build without pushing another commit, open the workflow in **Actions**, select **Run workflow**, choose `main`, and run it.

## Create a GitHub Release

### GitHub website

1. Update the pack's version file and the version displayed in its `pack.mcmeta`.
2. Commit and push the changes to `main`.
3. Open **Actions** → **Build resource packs** and wait for the run to succeed.
4. Download the Minecraft-ready ZIP for the pack being released:
   - `MagicalDreams-Generic-Pack-vX.Y.Z.zip`
   - `MagicalDreams-Parks-Pack-vX.Y.Z.zip`
5. Open **Releases** and select **Draft a new release**.
6. Create a pack-specific tag matching its version:
   - Generic: `generic-vX.Y.Z`
   - Parks: `parks-vX.Y.Z`
7. Target the `main` branch.
8. Use a title such as `MagicalDreams Parks Pack v2.1.0`.
9. Attach the downloaded Minecraft-ready ZIP.
10. Generate or write release notes, then select **Publish release**.

If both packs changed, create two releases with their respective tags and ZIPs.

### GitHub CLI

With [GitHub CLI](https://cli.github.com/) installed and authenticated:

```sh
version=$(<GENERIC_VERSION)
release_dir=$(mktemp -d)
gh run download --name "MagicalDreams-Generic-Pack-v${version}.zip" --dir "$release_dir"
gh release create "generic-v${version}" "$release_dir/MagicalDreams-Generic-Pack-v${version}.zip" \
  --title "MagicalDreams Generic Pack v${version}" \
  --generate-notes
```

For a Parks release, substitute `PARKS_VERSION`, `Parks`, and the `parks-v` tag prefix.

## Troubleshooting

- **No build appeared:** confirm the commit reached `main`, or run the workflow manually.
- **The workflow failed:** open its failed step in the Actions run for the full error.
- **Wrong version in a filename:** update and commit that pack's version file, then run a new build.
- **Wrong version in Minecraft:** update the `description` in that pack's `pack.mcmeta`.
- **Minecraft cannot detect the pack:** open the ZIP and confirm `pack.mcmeta` is at its root.
