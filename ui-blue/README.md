# Blue storybook UI — first pass

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

This is the approved first-pass scope. The player inventory screen, crafting/furnace screens, creative inventory, health/XP bars, and specialized controls can be adapted after reviewing this set.

## Compatibility and layout

Paths and dimensions were checked against the official Minecraft Java 1.21.1 and 26.2 client assets. The 26.2 client download was verified against its launcher manifest SHA-1. The standard chest renderer's UV stitching and slot coordinates were inspected in the 26.2 client. Intermediate versions have not all been launched or inspected individually.

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
- `original/` — original overwritten chest textures, backed up once per pack. Generated previews are outside runtime pack folders.

```sh
python3 ui-blue/draw_ui.py
python3 ui-blue/verify_ui.py
python3 scripts/build_packs.py
```

Both locally built packs are in `dist/`. Load one in Minecraft and reload resources with F3+T. Before deployment, check a short chest menu and a full six-row menu, hovered slots and tooltips, all nine hotbar selection positions, both offhand sides, and regular/hovered/disabled buttons at your normal GUI scale. Offline verification and visual preview review passed; the actual client has not been used for a rendering test in this task.
