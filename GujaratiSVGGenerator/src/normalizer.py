"""Geometry: font units -> a centered, upright 512x512 SVG path.

The whole point of this module is that we transform the *outline*, never the
SVG string.  Measure with a BoundsPen, build one affine transform, then pipe
the outline through a TransformPen into an SVGPathPen:

    outline -> BoundsPen -> transform -> TransformPen -> SVGPathPen -> "M..."
"""

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

from src import config


class EmptyOutlineError(Exception):
    """The outline has no drawable contours (e.g. a space)."""


def _formatter(decimals):
    def ntos(value):
        text = f"{round(value, decimals):.{decimals}f}"
        text = text.rstrip("0").rstrip(".")
        return "0" if text in ("", "-", "-0") else text

    return ntos


class Normalizer:
    def __init__(
        self,
        font,
        canvas=config.CANVAS_SIZE,
        padding=config.PADDING,
        fit_mode=config.FIT_MODE,
        decimals=config.DECIMALS,
    ):
        self.font = font
        self.glyph_set = font.glyph_set
        self.canvas = canvas
        self.padding = padding
        self.fit_mode = fit_mode
        self.ntos = _formatter(decimals)

    @property
    def available(self):
        return self.canvas - 2 * self.padding

    def bounds(self, outline):
        pen = BoundsPen(self.glyph_set)
        outline.draw(pen)
        if pen.bounds is None:
            raise EmptyOutlineError("outline has no contours")
        return pen.bounds

    def _scale(self, width, height):
        if self.fit_mode == "uniform":
            return self._uniform_scale()

        # "fit": grow the glyph until it touches the padded box on one axis.
        # Zero-extent axes (a perfectly flat outline) must not divide.
        candidates = [
            self.available / extent for extent in (width, height) if extent > 0
        ]
        if not candidates:
            raise EmptyOutlineError("outline has zero width and height")
        return min(candidates)

    def _uniform_scale(self):
        if not hasattr(self, "_cached_uniform"):
            hhea = self.font.ttfont["hhea"]
            extent = hhea.ascent - hhea.descent
            if extent <= 0:
                extent = self.font.units_per_em
            self._cached_uniform = self.available / extent
        return self._cached_uniform

    def extent(self, outline):
        """The outline's longest side, in font units."""
        x_min, y_min, x_max, y_max = self.bounds(outline)
        return max(x_max - x_min, y_max - y_min)

    def group_scales(self, outlines, cap=1.0):
        """One scale per outline, sized relative to the largest in the group.

        Members keep their true proportions to each other, except that a small
        member may be magnified up to `cap` times its proportional size so it
        is not lost on its own canvas.  No member ever overflows the box.
        """
        extents = [self.extent(o) for o in outlines]
        largest = max(extents)
        shared = self.available / largest
        ceiling = shared * cap
        return [min(self.available / e, ceiling) for e in extents]

    def transform(self, outline, scale=None):
        """The affine that maps this outline onto the canvas."""
        x_min, y_min, x_max, y_max = self.bounds(outline)

        width = x_max - x_min
        height = y_max - y_min
        if scale is None:
            scale = self._scale(width, height)

        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        canvas_center = self.canvas / 2

        # Read right to left: move the glyph's own center to the origin, scale
        # it (flipping Y, because font Y grows upward and SVG Y grows down),
        # then drop it on the middle of the canvas.
        return (
            Transform()
            .translate(canvas_center, canvas_center)
            .scale(scale, -scale)
            .translate(-center_x, -center_y)
        )

    def normalize(self, outline, scale=None):
        svg_pen = SVGPathPen(self.glyph_set, ntos=self.ntos)
        outline.draw(TransformPen(svg_pen, self.transform(outline, scale=scale)))
        return svg_pen.getCommands()
