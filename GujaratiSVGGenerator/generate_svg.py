"""Generate one 512x512 tracing SVG per Gujarati character, plus a manifest.

    python generate_svg.py                 # vowels + consonants + conjuncts
    python generate_svg.py --barakhadi     # ...plus every consonant x matra
    python generate_svg.py --clean         # wipe output/ first
"""

import argparse
import shutil
import sys
from pathlib import Path

from src import characters, config
from src.font_loader import load_font
from src.glyph_exporter import GlyphExporter
from src.manifest import ManifestBuilder
from src.normalizer import EmptyOutlineError, Normalizer
from src.shaper import MissingGlyphError
from src.svg_writer import SvgWriter


def use_utf8_console():
    """Windows consoles default to cp1252 and cannot print Gujarati."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--barakhadi", action="store_true",
                        help="also generate every consonant + matra syllable")
    parser.add_argument("--clean", action="store_true",
                        help="delete the output directory before generating")
    parser.add_argument("--out", type=Path, default=config.OUTPUT_DIR,
                        help=f"output directory (default: {config.OUTPUT_DIR.name})")
    parser.add_argument("--font", type=Path, default=config.FONT_PATH,
                        help="TTF/OTF to trace glyphs from")
    parser.add_argument("--canvas", type=int, default=config.CANVAS_SIZE,
                        help=f"canvas size in px (default: {config.CANVAS_SIZE})")
    parser.add_argument("--padding", type=int, default=config.PADDING,
                        help=f"padding in px (default: {config.PADDING})")
    parser.add_argument("--fit-mode", choices=("fit", "uniform"),
                        default=config.FIT_MODE,
                        help="'fit' maximises each glyph; 'uniform' shares one scale")
    parser.add_argument("--matra-style", choices=("both", "bare", "circle"),
                        default=config.MATRA_STYLE,
                        help="'bare' draws the mark alone, 'circle' puts it on a "
                             "dotted circle the way textbooks print it, 'both' "
                             "writes each to its own folder")
    parser.add_argument("--matra-scale-cap", type=float,
                        default=config.MATRA_SCALE_CAP,
                        help="how far a small bare mark may be magnified past its "
                             "true proportion (1.0 = strict proportion)")
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    return parser.parse_args(argv)


def plan_matra_scales(exporter, todo, cap):
    """Size the bare matras against each other, not against the canvas.

    Alone, the marks range over 7.6x in height - fitting each to the box would
    blow the anusvara dot up to the size of a full ી.  Scaling them as a group
    keeps that difference visible; the cap keeps the smallest ones traceable.
    """
    marks = [c.text for c in todo if c.category == "matra"]
    if not marks:
        return {}
    outlines = [exporter.outline(text, shape=False) for text in marks]
    return dict(zip(marks, exporter.normalizer.group_scales(outlines, cap=cap)))


def main(argv=None):
    use_utf8_console()
    args = parse_args(argv)

    if args.padding * 2 >= args.canvas:
        print(f"error: padding {args.padding} leaves no room on a "
              f"{args.canvas}px canvas", file=sys.stderr)
        return 2

    if args.clean and args.out.exists():
        shutil.rmtree(args.out)

    try:
        font = load_font(args.font)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    with font:
        if not args.quiet:
            print(font.describe())
            print("-" * 46)

        normalizer = Normalizer(font, canvas=args.canvas, padding=args.padding,
                                fit_mode=args.fit_mode)
        exporter = GlyphExporter(font, normalizer)
        writer = SvgWriter(args.out, canvas=args.canvas)
        manifest = ManifestBuilder(font, canvas=args.canvas, padding=args.padding,
                                   fit_mode=args.fit_mode)

        todo = characters.all_characters(include_barakhadi=args.barakhadi,
                                         matra_style=args.matra_style)
        matra_scales = plan_matra_scales(exporter, todo, args.matra_scale_cap)

        failures = []
        for character in todo:
            # Bare marks skip shaping (it would add a dotted circle) and take a
            # scale computed across the whole set.  Everything else, the
            # dotted-circle matras included, goes through the normal path.
            bare_matra = character.category == "matra"
            try:
                path_data = exporter.export(
                    character.text,
                    shape=not bare_matra,
                    scale=matra_scales.get(character.text) if bare_matra else None,
                )
            except (MissingGlyphError, EmptyOutlineError) as exc:
                failures.append((character, exc))
                print(f"  skipped {character.text} ({character.unicode}): {exc}",
                      file=sys.stderr)
                continue

            asset = Path(config.CATEGORY_DIRS[character.category]) / f"{character.slug}.svg"
            writer.write(asset, path_data)
            manifest.add(character, asset)

            if not args.quiet:
                print(f"  {character.text:<4} {character.unicode:<18} -> {asset.as_posix()}")

        manifest_path = manifest.write(args.out)

    print("-" * 46)
    for category, count in sorted(manifest.to_dict()["counts"].items()):
        print(f"{category:<12} {count:>4}")
    print(f"{'total':<12} {len(manifest.entries):>4} SVGs in {args.out}")
    print(f"manifest     {manifest_path}")

    if failures:
        print(f"\n{len(failures)} character(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
