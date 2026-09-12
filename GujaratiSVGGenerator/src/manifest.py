"""Builds manifest.json - the bridge between ASCII filenames and Gujarati text.

Files are named by code point (u0A95_u0ABE.svg) so they survive ZIPs, CI and
asset bundlers unchanged; the Flutter app reads the real character from here.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src import config


class ManifestBuilder:
    def __init__(self, font, canvas=config.CANVAS_SIZE, padding=config.PADDING,
                 fit_mode=config.FIT_MODE):
        self.font = font
        self.canvas = canvas
        self.padding = padding
        self.fit_mode = fit_mode
        self.entries = []

    def add(self, character, asset_path):
        self.entries.append(
            {
                "character": character.text,
                "unicode": character.unicode,
                "label": character.label,
                "category": character.category,
                "file": Path(asset_path).name,
                "path": str(asset_path).replace("\\", "/"),
            }
        )

    def to_dict(self):
        counts = {}
        for entry in self.entries:
            counts[entry["category"]] = counts.get(entry["category"], 0) + 1

        return {
            "version": 1,
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "font": self.font.path.name,
            "canvas": {"width": self.canvas, "height": self.canvas,
                       "padding": self.padding, "fitMode": self.fit_mode},
            "fill": config.FILL,
            "total": len(self.entries),
            "counts": counts,
            "characters": self.entries,
        }

    def write(self, output_dir, name=config.MANIFEST_NAME):
        target = Path(output_dir) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return target
