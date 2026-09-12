# Gujarati Tracing SVG Generator

Turns a Gujarati font into one 512×512 SVG per character, ready to drop into a
Flutter tracing game.

```bash
pip install -r requirements.txt
python generate_svg.py
```

## Output

```
output/
├── vowels/       u0A85.svg …                 13
├── consonants/   u0A95.svg …                 34
├── combined/     u0A95_u0ACD_u0AB7.svg …      2
├── special/      u0AAA_u0ACD_u0AB0.svg …      7   ligatures & reph forms
├── matras/       u0ABE.svg …                 11   bare marks
├── matras_circle/u0ABE.svg …                 11   marks on a dotted circle
└── manifest.json
```

Add `--barakhadi` for every consonant × matra syllable (374 more, in
`output/barakhadi/`).

Files are named by code point so they survive ZIPs, CI and asset bundlers
unchanged. The Gujarati character itself lives in `manifest.json`:

```json
{
  "character": "ક્ષ",
  "unicode": "U+0A95 U+0ACD U+0AB7",
  "label": "ksha",
  "category": "combined",
  "file": "u0A95_u0ACD_u0AB7.svg",
  "path": "combined/u0A95_u0ACD_u0AB7.svg"
}
```

Every SVG is 512×512, centered on (256, 256), padded 40px, and uses
`fill="currentColor"` so Flutter can recolor it.

## Options

| Flag | Default | |
|---|---|---|
| `--barakhadi` | off | also generate consonant + matra syllables |
| `--clean` | off | wipe `output/` first |
| `--out DIR` | `output` | output directory |
| `--font FILE` | `fonts/NotoSansGujarati-Regular.ttf` | source font |
| `--canvas PX` | 512 | canvas size |
| `--padding PX` | 40 | padding |
| `--fit-mode` | `fit` | `fit` maximises each glyph; `uniform` shares one scale across all |
| `--matra-style` | `both` | `bare`, `circle`, or `both` in separate folders |
| `--matra-scale-cap` | `2.0` | how far a small bare mark may be magnified past true proportion |

Defaults live in [config.py](src/config.py).

## Special forms

`special/` holds clusters whose written shape is not their parts side by side:

| | | shaped result |
|---|---|---|
| પ્ર ક્ર શ્ર ત્ર | pra kra shra tra | one dedicated ligature each (`paragujr`, `karagujr`, …) |
| રૂ | ruu | `rauuvowelgujr`, the irregular ra + ū form |
| ર્વ | rva | ra lifted onto the roof as a reph |
| પૃ | pru | pa + the vocalic-r matra ૃ |

None of these needed special-casing in code — HarfBuzz produces the right
glyphs from the plain code point sequence. They are listed separately only
because they are taught as forms in their own right.

## Matras

Vowel signs are combining marks, which makes them a special case twice over.

**Shaping adds a dotted circle.** Ask HarfBuzz to shape a lone `ા` and it
correctly returns `U+25CC + mark` — that is how primers print matras, showing
where the consonant goes. Both forms are generated: `matras/` skips shaping and
reads the glyph straight from cmap, `matras_circle/` keeps the shaped result.
Same filename in each, so switching the folder switches the style.

**The marks differ in size by 7.6×.** `ી` is 896 font units tall; the anusvara
`ં` is 118. Fitting each to the box would blow that dot up to the size of a full
letter. Bare matras are therefore scaled as a *group*, so their relative sizes
survive, with `--matra-scale-cap` letting the smallest ones grow enough to stay
traceable. The dotted-circle style needs none of this — the circle equalises
them on its own.

## How it works

```
text  →  Shaper (HarfBuzz)  →  positioned glyphs
                                     ↓
                              ShapedOutline
                                     ↓
                     BoundsPen  →  Transform  →  TransformPen  →  SVGPathPen
                                     ↓
                                 <path d="…">
```

The geometry is transformed *before* the SVG is written — there is no
string rewriting anywhere. Shaping runs the font's real GSUB/GPOS tables, which
is why conjuncts (`ક્ષ`) collapse correctly and the i-matra in `કિ` lands to the
left of its consonant.

| Module | Job |
|---|---|
| [config.py](src/config.py) | constants |
| [characters.py](src/characters.py) | the character set + romanisations |
| [font_loader.py](src/font_loader.py) | one font, two views (fontTools + HarfBuzz) |
| [shaper.py](src/shaper.py) | text → positioned glyphs |
| [glyph_exporter.py](src/glyph_exporter.py) | positioned glyphs → one drawable outline |
| [normalizer.py](src/normalizer.py) | measure, scale, center, flip Y |
| [svg_writer.py](src/svg_writer.py) | write the SVG file |
| [manifest.py](src/manifest.py) | write `manifest.json` |

`unicode_mapper.py` is a leftover from the prototype — shaping replaced it.
`scripts/` is the earlier FontForge experiment and is not used.

## Using it in Flutter

```yaml
flutter:
  assets:
    - assets/glyphs/
```

Read `manifest.json`, then render `path` with `flutter_svg`. Because the fill is
`currentColor`, wrapping the widget in a themed color changes the trace color.
