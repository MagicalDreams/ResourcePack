# Blue storybook UI

A shared, hand-drawn pixel interface for Generic RP and Parks RP: navy outlines, muted blue surfaces, pale blue label bands, recessed slate slots, sky-blue focus, and tiny gold corner accents. The gold menu-item icons provide the strongest accent color.

## Included

All paths below are relative to `assets/minecraft/textures/gui/` in each pack.

| Texture | Native size | Purpose |
| --- | --- | --- |
| `container/generic_54.png` | 256×256 | Standard chest menus, automatically assembled for 1–6 rows |
| `sprites/hud/hotbar.png` | 182×22 | Nine-slot hotbar |
| `sprites/hud/hotbar_selection.png` | 24×23 | Sky-blue selected-slot frame, gold corners, transparent item window |
| `sprites/hud/hotbar_offhand_left.png` | 29×24 | Left offhand frame with vanilla padding |
| `sprites/hud/hotbar_offhand_right.png` | 29×24 | Right offhand frame with vanilla padding |
| `sprites/widget/button.png` | 200×20 | Normal standard button |
| `sprites/widget/button_highlighted.png` | 200×20 | Hover/focus state |
| `sprites/widget/button_disabled.png` | 200×20 | Disabled state |

The three button textures include explicit nine-slice metadata with a 3px border. Decorations stay in the fixed corners, so narrow and wide controls retain their shape. This standard button system has normal, highlighted, and disabled textures; it does not provide a separate pressed texture.

The expansion adds 251 PNGs and 30 scaling sidecars to each pack:

- Player and creative inventories, creative tabs/search/scrolling, shulker boxes, horse and nautilus inventories.
- Crafting, furnace, blast furnace, smoker, anvil, hopper, dispenser/dropper, trading, enchanting, brewing, beacon, smithing, stonecutter, loom, grindstone, cartography and crafter screens and their controls.
- Recipe book panels, tabs, filters and recipe states; text fields, checkboxes, sliders, scrollbars, tabs and lock controls.
- Tooltip frames and advancement, recipe, tutorial and system notifications.
- F3+F4 game-mode selector and slot states, book background, tiled menu/list backgrounds and header/footer separators. The book retains light pages for dark writing; menu tiles retain their native translucency.

Optional HUD artwork such as health, hunger, armor and XP is excluded. The previously approved hotbar is unchanged.

## Compatibility and layout

Paths and dimensions were checked against the official Minecraft Java 1.21.1 and 26.2 client assets. The 26.2 client download was verified against its launcher manifest SHA-1. The standard chest renderer's UV stitching and slot coordinates were inspected in the 26.2 client. Intermediate versions have not all been launched or inspected individually. Templates in `templates/` preserve official dimensions, silhouettes and item coordinates; `templates/manifest.json` records provenance. The expansion is a palette and pixel-detail adaptation of these native layouts.

System notifications use the legacy 160×32 source with explicit nine-slice metadata, supporting both the older manual UV assembly and newer stretched panels. Minecraft 1.21.1 draws tooltip frames in code and does not use the newer tooltip sprites, so those clients retain their vanilla tooltip frame. No shader override is included.

The existing packs' `widgets.png` files are older atlases. Modern supported clients use the individual `sprites/` overrides added here; the old atlases are not the authoring source for these controls.

Chest slots retain their vanilla 18px pitch and 16×16 item windows. The renderer joins the first `rows*18+17` pixels to a 96px strip starting at atlas Y=126. The preview uses this exact assembly, rather than displaying the atlas as a single cropped image. The 256px atlas is authored at native GUI resolution; all preview enlargement uses nearest-neighbor scaling.

Dark vanilla chest labels remain readable against the pale blue bands. No labels, button text, or item names are baked into these PNGs. Minecraft, the resource pack's font, and the menu plugin still control the displayed text and text colors. Preview lettering and item placements are illustrative, not an in-game screenshot or plugin configuration.

Resource-pack overrides apply to all standard chest menus using this texture, not just the server selector. Ordinary buttons using the standard widget sprites also receive the theme.

## Review and regenerate

- `preview.png` — composed first-pass review of the chest, buttons, navigation items, and hotbar.
- `chest-heights.png` — the six standard chest heights.
- `draw_ui.py` — authoritative pixel drawing code and preview assembly.
- `palette.json` — named palette colors generated from that code.
- `verify_ui.py` — coordinate, transparency, scaling, and matching-pack checks.
- `expansion-preview.png` — compact overview of the additional screen backgrounds.
- `review-containers.png`, `review-creative-recipes.png`, `review-controls.png` — detailed category reviews including control states.
- `draw_all_ui.py` — exports the original set plus all three expansion generators.
- `draw_containers.py`, `draw_creative_recipes.py`, `draw_controls.py`, `draw_menu_surfaces.py` — category artwork generators.
- `verify_expansion.py` — exact dimensions/alpha, 1,006 item windows, 27 hover pairs, metadata, matching-pack and unchanged-HUD checks.
- `review-menu-surfaces.png` — book, game-mode selector and tiled menu preview.
- `expansion-manifest.json` — complete exported asset inventory.
- `original/` — overwritten files backed up once per pack. Generated previews are outside runtime pack folders.

```sh
python3 ui-blue/draw_all_ui.py
python3 ui-blue/preview_expansion.py
python3 ui-blue/verify_ui.py
python3 ui-blue/verify_expansion.py
python3 scripts/build_packs.py
```

Both locally built packs are in `dist/`. Load one in Minecraft and reload resources with F3+T. Before deployment, check a short chest menu and a full six-row menu, hovered slots and tooltips, all nine hotbar selection positions, both offhand sides, and regular/hovered/disabled buttons at your normal GUI scale. Also check workstation progress, creative search/tabs, recipe availability, trading, tooltip text and notifications. Offline verification and visual preview review passed; the actual client has not been used for a rendering test in this task.
