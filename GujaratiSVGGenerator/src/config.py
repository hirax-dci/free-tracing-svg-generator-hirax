"""Central configuration for the Gujarati tracing-SVG generator."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FONT_PATH = PROJECT_ROOT / "fonts" / "NotoSansGujarati-Regular.ttf"
OUTPUT_DIR = PROJECT_ROOT / "output"

# --- Canvas -----------------------------------------------------------------

CANVAS_SIZE = 512
PADDING = 40

# --- Scaling ----------------------------------------------------------------
#
# "fit"     each character is scaled individually so it fills the padded box.
#           Biggest possible glyph on every card - best for tracing.
#
# "uniform" every character shares one scale derived from the font's em box.
#           Relative sizes stay true to the typeface (ક smaller than કી), but
#           short glyphs look small on the canvas.
#
FIT_MODE = "fit"

# --- Matras -----------------------------------------------------------------
#
# "bare"   the mark on its own, straight from cmap (no shaping).
# "circle" the mark on a dotted circle, the way textbooks print it.
# "both"   both, in separate folders.
#
MATRA_STYLE = "both"

# Bare marks are scaled together so they keep their relative sizes, but the
# smallest (the anusvara dot, 1/7.6 the height of the tallest mark) would be
# unusably small on its own card.  This caps how far a small mark may be
# magnified beyond its true proportion.  1.0 = strict proportion.
MATRA_SCALE_CAP = 2.0

# --- Output -----------------------------------------------------------------

FILL = "currentColor"
DECIMALS = 2          # coordinate precision in the `d` attribute
MANIFEST_NAME = "manifest.json"

# --- Shaping ----------------------------------------------------------------

SCRIPT = "Gujr"
LANGUAGE = "gu"
DIRECTION = "ltr"

# Sub-directory per category.
CATEGORY_DIRS = {
    "vowel": "vowels",
    "consonant": "consonants",
    "combined": "combined",
    "special": "special",
    "matra": "matras",
    "matra_circle": "matras_circle",
    "barakhadi": "barakhadi",
}
