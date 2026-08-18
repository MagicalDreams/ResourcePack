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

## Change the pack version

`VERSION` controls the version in generated ZIP filenames and the GitHub Actions artifact name.

1. Update `VERSION`, for example:

   ```text
   2.1.0
   ```

2. Update the displayed version in both pack metadata files:

   - `Generic RP/pack.mcmeta`
   - `Parks RP/pack.mcmeta`

3. Commit the version together with the pack changes:

   ```sh
   git add VERSION "Generic RP/pack.mcmeta" "Parks RP/pack.mcmeta"
   git commit -m "Release version 2.1.0"
   git push origin main
   ```

Use patch versions for fixes (`2.0.1`), minor versions for compatible additions (`2.1.0`), and major versions for breaking changes (`3.0.0`).

## Validate locally

Check the metadata JSON:

```sh
jq empty "Generic RP/pack.mcmeta" "Parks RP/pack.mcmeta"
```

Build the same versioned ZIPs produced by GitHub Actions:

```sh
version=$(<VERSION)
mkdir -p dist
rm -f "dist/MagicalDreams-Generic-Pack-v${version}.zip" \
      "dist/MagicalDreams-Parks-Pack-v${version}.zip"
(cd "Generic RP" && zip -r "../dist/MagicalDreams-Generic-Pack-v${version}.zip" . -x '*.DS_Store')
(cd "Parks RP" && zip -r "../dist/MagicalDreams-Parks-Pack-v${version}.zip" . -x '*.DS_Store')
unzip -t "dist/MagicalDreams-Generic-Pack-v${version}.zip"
unzip -t "dist/MagicalDreams-Parks-Pack-v${version}.zip"
```

Each ZIP must contain `pack.mcmeta` at its root, not inside another folder.

## Get a new build from GitHub Actions

Every push to `main` automatically runs **Build resource packs**.

1. Open the repository's **Actions** tab.
2. Select **Build resource packs**.
3. Open the latest successful run.
4. Download `MagicalDreams-resource-packs-vX.Y.Z` under **Artifacts**.
5. Extract the downloaded artifact to get the Generic and Parks pack ZIPs.

To build without pushing another commit, open the workflow in **Actions**, select **Run workflow**, choose `main`, and run it.

## Create a GitHub Release

### GitHub website

1. Download and extract the successful Actions artifact.
2. Open **Releases** and select **Draft a new release**.
3. Create a tag matching `VERSION`, prefixed with `v` (for example, `v2.1.0`).
4. Target the `main` branch.
5. Use a title such as `MagicalDreams Resource Packs v2.1.0`.
6. Attach the two inner resource-pack ZIPs.
7. Generate or write release notes, then publish the release.

Do not attach the outer Actions artifact ZIP; attach the two Minecraft-ready ZIPs inside it.

### GitHub CLI

With [GitHub CLI](https://cli.github.com/) installed and authenticated:

```sh
version=$(<VERSION)
mkdir -p release-assets
gh run download --name "MagicalDreams-resource-packs-v${version}" --dir release-assets
gh release create "v${version}" release-assets/*.zip \
  --title "MagicalDreams Resource Packs v${version}" \
  --generate-notes
```

## Troubleshooting

- **No build appeared:** confirm the commit reached `main`, or run the workflow manually.
- **The workflow failed:** open its failed step in the Actions run for the full error.
- **Wrong version in a filename:** update and commit `VERSION`, then run a new build.
- **Wrong version in Minecraft:** update the `description` in both `pack.mcmeta` files.
- **Minecraft cannot detect the pack:** open the ZIP and confirm `pack.mcmeta` is at its root.
