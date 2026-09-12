"""Text -> positioned glyphs, via HarfBuzz.

A cmap lookup is not enough for Gujarati: `અં` is two code points, `ક્ષ`
collapses three into one conjunct glyph, and every matra in `કી` carries its
own placement.  HarfBuzz runs the font's real GSUB/GPOS tables, so what we
draw is exactly what the text engine would draw.
"""

from dataclasses import dataclass

import uharfbuzz as hb

from src import config


class MissingGlyphError(Exception):
    """The font has no outline for part of this character."""


@dataclass(frozen=True)
class Placement:
    glyph_name: str
    x: float
    y: float


class Shaper:
    def __init__(self, font):
        self.font = font

    def shape(self, text):
        """Return the glyphs that render `text`, in font units."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = config.DIRECTION
        buf.script = config.SCRIPT
        buf.language = config.LANGUAGE

        hb.shape(self.font.hb_font, buf, {})

        placements = []
        pen_x = pen_y = 0.0

        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            if info.codepoint == 0:
                raise MissingGlyphError(
                    f"{text!r} shapes to .notdef - the font lacks this character"
                )

            placements.append(
                Placement(
                    glyph_name=self.font.glyph_name(info.codepoint),
                    x=pen_x + pos.x_offset,
                    y=pen_y + pos.y_offset,
                )
            )

            pen_x += pos.x_advance
            pen_y += pos.y_advance

        if not placements:
            raise MissingGlyphError(f"{text!r} produced no glyphs")

        return placements
