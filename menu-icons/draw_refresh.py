"""Compatibility entry point: regenerate the complete navigation family."""
from draw_navigation import sprites, preview, export

if __name__ == "__main__":
    icons = sprites()
    preview(icons)
    export(icons)
