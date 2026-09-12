"""Loads the font once and hands out both views we need of it.

fontTools gives us outlines; HarfBuzz gives us shaping.  They have to be
built from the same file, so they live together in one bundle.
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

from src import config


class FontBundle:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Font not found: {self.path}")

        self.ttfont = TTFont(self.path)
        self.glyph_set = self.ttfont.getGlyphSet()
        self.glyph_order = self.ttfont.getGlyphOrder()
        self.units_per_em = self.ttfont["head"].unitsPerEm
        self._cmap = None

        blob = hb.Blob.from_file_path(str(self.path))
        face = hb.Face(blob)
        self.hb_font = hb.Font(face)

    def glyph_name(self, glyph_id):
        return self.glyph_order[glyph_id]

    def glyph_name_for_char(self, char):
        """Straight cmap lookup, no shaping.

        Needed for combining marks: shaping an isolated matra correctly adds a
        dotted circle (U+25CC), which we do not want on a bare-mark card.
        """
        if self._cmap is None:
            self._cmap = self.ttfont.getBestCmap()
        return self._cmap.get(ord(char))

    def describe(self):
        return (
            f"Font        : {self.path.name}\n"
            f"Glyphs      : {len(self.glyph_order)}\n"
            f"Units per em: {self.units_per_em}"
        )

    def close(self):
        self.ttfont.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def load_font(path=None):
    return FontBundle(path or config.FONT_PATH)
