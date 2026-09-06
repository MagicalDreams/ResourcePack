# Tintable spotlight beam

Editable source: `spotlight_beam.bbmodel`. Java model: `spotlight_beam.json`. Texture: `spotlight_beam.png` (128 × 256 RGBA, neutral white).

Four double-sided crossed planes, 8 rendered faces, soft tapered transparency. Beam points down local -Y; it is 2 blocks long and up to 1 block wide at scale 1. The fixed display transform places the narrow source at the item-display origin. No fixture or collision is included.

## Editing and keeping both packs in sync

Edit `spotlight_beam.bbmodel` in Blockbench. The texture is embedded and also provided alongside the project. Export the Java model to `spotlight_beam.json`, keeping namespace `spotlight` and texture folder `item`. Copy the exported model and texture into **both** pack folders at `assets/spotlight/models/item/spotlight_beam.json` and `assets/spotlight/textures/item/spotlight_beam.png`. Preserve tint index 0 on every visible face. The companion `assets/spotlight/items/spotlight_beam.json` in each pack supplies the runtime tint mapping and must be kept identical as well; it is separate from the Blockbench model export.

## Modern resource pack and runtime color (Java 1.21.4+)

The active exports are installed in both `Generic RP/assets/spotlight` and `Parks RP/assets/spotlight` at the repository root. Both packs retain their existing Minecraft version metadata. The beam uses the custom item model / RGB tint system and requires Java 1.21.4 or newer; it is not available through this mechanism on the packs' older supported clients.

The standalone `modern-1.21.8` and `legacy-1.20.4` folders and ZIPs are retained as original reference exports. They are outside the pack roots and are not included in repository builds.

Model component ID: `spotlight:spotlight_beam`. Model resource location: `spotlight:item/spotlight_beam`.
All rendered faces use tint index 0. The item definition reads `minecraft:custom_model_data.colors[0]`, defaulting to white. Colors use packed 24-bit RGB: `(red << 16) | (green << 8) | blue`.

Give yourself a cyan beam:

```mcfunction
/give @s minecraft:white_stained_glass[minecraft:item_model="spotlight:spotlight_beam",minecraft:custom_model_data={colors:[65535]}]
```

Spawn a cyan beam pointing downward, with its source 4 blocks above you. The Y scale of 2 makes it 4 blocks long:

```mcfunction
/summon minecraft:item_display ~ ~4 ~ {Tags:["spotlight_beam"],billboard:"fixed",item_display:"fixed",brightness:{block:15,sky:15},shadow_radius:0f,width:4f,height:8f,transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],scale:[1f,2f,1f],right_rotation:[0f,0f,0f,1f]},item:{id:"minecraft:white_stained_glass",count:1,components:{"minecraft:item_model":"spotlight:spotlight_beam","minecraft:custom_model_data":{colors:[65535]}}}}
```

Recolor the nearest tagged beam to red without respawning it:

```mcfunction
/data modify entity @e[type=minecraft:item_display,tag=spotlight_beam,sort=nearest,limit=1] item.components."minecraft:custom_model_data".colors set value [16711680]
```

RGB examples: white 16777215; red 16711680; green 65280; blue 255; cyan 65535; magenta 16711935; amber 16756736.

Plugin integration: set the ItemStack's item-model component to `spotlight:spotlight_beam`, set custom-model-data colors to your desired RGB color, then assign the updated ItemStack back to the ItemDisplay. Use FIXED display transform, fixed billboard, brightness 15/15, and zero shadow. Rotate using the display transformation quaternion; scale local Y for length and local X/Z for width. Increasing both X/Z together keeps the beam round from different side angles. Only the item contents need updating for a color change; the resource pack stays the same. Actual API calls depend on your Paper/Spigot version; no plugin source was modified.

## Legacy white-only fallback (Java 1.20.4)

`legacy-1.20.4.zip` uses custom model data 91001 on white stained glass. Merge its override carefully if your resource pack already customizes that item. It does **not** provide runtime RGB tint; use the modern pack for that feature.

```mcfunction
/give @s minecraft:white_stained_glass{CustomModelData:91001}
```

## Rendering and validation

This is a translucent crossed-plane beam effect, not a solid cone mesh or a real light source. Full display brightness keeps the beam visible in darkness but does not light surrounding blocks. Transparency/sorting can vary with shaders, client versions, and overlapping displays. The far end fades away rather than forming a floor spot. Viewed exactly down its axis, crossed planes become edge-on.

JSON structure, geometry bounds, texture paths, UVs, tint mapping, and ZIP integrity were checked. In-game rendering and server commands have not been tested on a running server.

Official tint specification: https://feedback.minecraft.net/hc/en-us/articles/32385811139085-Minecraft-Java-Edition-1-21-4-The-Garden-Awakens
