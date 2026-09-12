import subprocess
from pathlib import Path

FONTFORGE = r"C:\Program Files\FontForgeBuilds\bin\fontforge.exe"

ROOT = Path(__file__).resolve().parent.parent

FONT = ROOT / "fonts" / "NotoSansGujarati-Regular.ttf"

SCRIPT = ROOT / "scripts" / "export_one.pe"

result = subprocess.run(
    [
        FONTFORGE,
        "-script",
        str(SCRIPT),
        str(FONT),
    ],
    capture_output=True,
    text=True,
)

print(result.stdout)
print(result.stderr)