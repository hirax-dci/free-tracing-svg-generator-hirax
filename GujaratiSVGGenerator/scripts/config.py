from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FONTFORGE = r"C:\Program Files\FontForgeBuilds\bin\fontforge.exe"

FONT_FILE = PROJECT_ROOT / "fonts" / "NotoSansGujarati-Regular.ttf"

OUTPUT_DIR = PROJECT_ROOT / "output"

VIEWBOX_SIZE = 512