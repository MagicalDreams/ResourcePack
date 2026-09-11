# Chest GUI menu icons

Eight transparent 64×64 PNG item textures are included identically in `Generic RP` and `Parks RP`.

| Menu entry | Artwork | Item model ID |
| --- | --- | --- |
| Hub | Gold and cyan compass | `magicaldreams:menu/hub` |
| Disneyland | Pink Sleeping Beauty Castle | `magicaldreams:menu/disneyland` |
| Walt Disney World | Ivory castle with tall blue spires | `magicaldreams:menu/walt_disney_world` |
| Creative | Grass block and builder's hammer | `magicaldreams:menu/creative` |
| Back | Gold left arrow | `magicaldreams:menu/back` |
| Next | Exact horizontal flip of Back | `magicaldreams:menu/next` |
| Close | Gold X | `magicaldreams:menu/close` |
| Refresh | Stacked opposing gold arrows | `magicaldreams:menu/refresh` |

## Usage

For Minecraft Java 1.21.4+, set the menu item's `minecraft:item_model` component to the ID above. For example:

```mcfunction
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/hub"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/disneyland"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/walt_disney_world"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/creative"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/back"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/next"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/close"]
/give @s minecraft:paper[minecraft:item_model="magicaldreams:menu/refresh"]
```

For your custom Bukkit/Paper plugin, use `ItemMeta#setItemModel`:

```java
ItemStack icon = new ItemStack(Material.PAPER);
ItemMeta meta = icon.getItemMeta();
meta.setItemModel(new NamespacedKey("magicaldreams", "menu/hub"));
icon.setItemMeta(meta);
```

Replace `menu/hub` with another path from the table. Imports are `org.bukkit.Material`, `org.bukkit.NamespacedKey`, `org.bukkit.inventory.ItemStack`, and `org.bukkit.inventory.meta.ItemMeta`. See the [Paper API reference](https://jd.papermc.io/paper/26.2/org/bukkit/inventory/meta/ItemMeta.html#setItemModel(org.bukkit.NamespacedKey)). No numeric CustomModelData value is required.

Configure display names, lore, destinations, and click actions in your custom plugin. The resource pack provides appearance only.

These icons use the [item model definition system introduced in Java 1.21.4](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-4). They do not add legacy CustomModelData mappings for 1.21.1–1.21.3, despite the wider compatibility range of the packs themselves.

## Files and editing

Within each pack, the namespace is `assets/magicaldreams`:

- `textures/item/menu/*.png` — runtime textures.
- `models/item/menu/*.json` — flat generated item models with front GUI lighting.
- `items/menu/*.json` — item model definitions.

The four server icons use simplified edits of the original artwork: fewer decorations, broader shading and a 32×32 pixel grid exported at 64×64. Their subjects and model IDs are unchanged. The original artwork remains in `source/`; the original prompts remain in `prompts.json`.

`python3 menu-icons/simplified/export.py` reproduces the current exports and `simplified/comparison.png`, which shows before/after at 16, 32 and 64 pixels plus enlargement. Edited source images and built-in image-generation prompts are saved in `simplified/`. The normalization script removes the generated opaque checkerboard background, reduces shading without dithering and preserves transparent padding. `*-before.png` files preserve the prior runtime textures.

Back, Next, Close, and Refresh are authored by `python3 menu-icons/draw_navigation.py`. This script is their authoritative source: a fixed 32×32 grid, a shared six-color gold/navy palette, a one-pixel outline and consistent bevel shading. Next is an exact horizontal flip of the finished Back texture, including shading, as requested.

The script writes `source/{name}-grid.png`, a labeled `navigation-preview.png` showing the set at 16px, 32px, 64px and enlarged sizes, and matching 64×64 nearest-neighbor exports plus model definitions in both packs. Refresh uses two equally sized stacked arrows: right above, left below. Their geometry is related by an exact 180-degree rotation, with a transparent gap between them. The older generated PNGs and refresh prompts are retained as historical references, not runtime sources. `draw_refresh.py` forwards to the new generator so it cannot restore the obsolete design.

Build with `python3 scripts/build_packs.py`. Reload resources in Minecraft and inspect the items in your actual chest menu before deploying; offline checks cannot verify the final in-game appearance.
