"""Writes one minimal, Flutter-ready SVG per character."""

from pathlib import Path

from src import config

TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
    '<path d="{path}" fill="{fill}"/>'
    "</svg>\n"
)


class SvgWriter:
    def __init__(self, output_dir, canvas=config.CANVAS_SIZE, fill=config.FILL):
        self.output_dir = Path(output_dir)
        self.canvas = canvas
        self.fill = fill

    def write(self, relative_path, path_data):
        target = self.output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            TEMPLATE.format(size=self.canvas, path=path_data, fill=self.fill),
            encoding="utf-8",
        )
        return target
