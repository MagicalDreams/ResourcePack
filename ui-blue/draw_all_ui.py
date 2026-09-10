"""Build the complete blue UI in both packs; preserve layout and sprite metadata."""
from pathlib import Path
import json
import shutil
import stat
from PIL import Image
import draw_ui
import draw_containers
import draw_controls
import draw_creative_recipes
import draw_menu_surfaces

ROOT=draw_ui.ROOT
HERE=ROOT/'ui-blue'
TEMPLATES=HERE/'templates'


def expanded_assets():
    combined={}
    for module in (draw_containers,draw_controls,draw_creative_recipes,draw_menu_surfaces):
        group=module.assets()
        overlap=combined.keys() & group.keys()
        if overlap:raise ValueError(f'Conflicting ownership: {overlap}')
        combined.update(group)
    if any(name.startswith('sprites/hud/') for name in combined):
        raise ValueError('The expansion must not change HUD textures')
    return combined


def metadata():
    result={}
    for name in expanded_assets():
        sidecar=TEMPLATES/(name+'.mcmeta')
        if sidecar.exists():result[name]=json.loads(sidecar.read_text())
    result.update(draw_controls.metadata_overrides())
    return result


def writable_destination(path,root):
    # Older pack files/directories were checked out with owner write disabled.
    # Limit permission adjustments to explicit destinations inside each GUI root.
    current=path.parent
    while current==root or root in current.parents:
        if current.exists():current.chmod(current.stat().st_mode|stat.S_IWUSR)
        if current==root:break
        current=current.parent
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():path.chmod(path.stat().st_mode|stat.S_IWUSR)


def save_with_backup(path,root,writer):
    if path.exists():
        # root is <pack>/assets/minecraft/textures/gui.
        pack=root.relative_to(ROOT).parts[0]
        backup=HERE/'original'/pack/path.relative_to(root)
        if not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,backup)
    writable_destination(path,root)
    writer(path)


def export():
    output=expanded_assets()
    sidecars=metadata()
    for pack in draw_ui.PACKS:
        root=ROOT/pack/'assets/minecraft/textures/gui'
        for name,im in output.items():
            save_with_backup(root/name,root,lambda p,im=im:im.save(p))
            if name in sidecars:
                payload=json.dumps(sidecars[name],indent=2)+'\n'
                save_with_backup(root/(name+'.mcmeta'),root,lambda p,s=payload:p.write_text(s))
    manifest={name:{'size':list(im.size),'metadata':name in sidecars} for name,im in sorted(output.items())}
    (HERE/'expansion-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return output



if __name__=='__main__':
    # Original first-pass controls remain authoritative in draw_ui.py.
    original=draw_ui.assets()
    draw_ui.preview(original)
    draw_ui.export(original)
    expanded=export()
    # Render each category once, without re-evaluating a generator per asset.
    draw_containers.preview(draw_containers.assets())
    draw_controls.preview(draw_controls.assets())
    draw_creative_recipes.review(draw_creative_recipes.assets())
    draw_menu_surfaces.preview(draw_menu_surfaces.assets())
    print(f'Exported {len(expanded)} additional PNGs and {len(metadata())} metadata files per pack.')
