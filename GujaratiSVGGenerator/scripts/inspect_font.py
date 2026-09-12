import subprocess

from config import FONTFORGE, FONT_FILE

script = f"""
import fontforge

font = fontforge.open(r"{FONT_FILE}")

print("=" * 60)
print("Font Information")
print("=" * 60)

print("Family :", font.familyname)
print("Full   :", font.fullname)
print("Em Size:", font.em)

glyphs = list(font.glyphs())

print("\\nTotal Glyphs:", len(glyphs))

print("\\nFirst 25 glyphs")

for glyph in glyphs[:25]:
    print(
        glyph.glyphname,
        glyph.unicode
    )

font.close()
"""

result = subprocess.run(
    [
        FONTFORGE,
        "-lang=py",
        "-c",
        script,
    ],
    capture_output=True,
    text=True,
)

print(result.stdout)

print(result.stderr)