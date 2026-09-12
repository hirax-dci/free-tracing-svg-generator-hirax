"""Shaped glyphs -> one drawable outline -> one normalized SVG path."""

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen

from src.normalizer import Normalizer
from src.shaper import MissingGlyphError, Placement, Shaper


class ShapedOutline:
    """Several positioned glyphs presented as a single drawable shape.

    Exposes the same `draw(pen)` contract as a plain glyph, so the normalizer
    does not care whether it is measuring `ક` or `ક્ષ`.
    """

    def __init__(self, glyph_set, placements):
        self.glyph_set = glyph_set
        self.placements = placements

    def draw(self, pen):
        for placement in self.placements:
            glyph = self.glyph_set[placement.glyph_name]
            if placement.x or placement.y:
                glyph.draw(
                    TransformPen(pen, Transform().translate(placement.x, placement.y))
                )
            else:
                glyph.draw(pen)


class GlyphExporter:
    def __init__(self, font, normalizer=None):
        self.font = font
        self.glyph_set = font.glyph_set
        self.shaper = Shaper(font)
        self.normalizer = normalizer or Normalizer(font)

    def outline(self, text, shape=True):
        """Build the drawable outline for `text`.

        With shape=False the glyphs come straight from cmap.  That is only
        right for isolated combining marks, where shaping would helpfully add
        a dotted circle we do not want.
        """
        if shape:
            return ShapedOutline(self.glyph_set, self.shaper.shape(text))

        placements = []
        for char in text:
            name = self.font.glyph_name_for_char(char)
            if name is None:
                raise MissingGlyphError(f"{char!r} (U+{ord(char):04X}) is not in the font")
            placements.append(Placement(glyph_name=name, x=0.0, y=0.0))
        return ShapedOutline(self.glyph_set, placements)

    def export(self, text, shape=True, scale=None):
        """Return the SVG `d` attribute for `text`, centered on the canvas."""
        return self.normalizer.normalize(self.outline(text, shape=shape), scale=scale)
