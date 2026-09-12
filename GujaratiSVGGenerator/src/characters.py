"""The Gujarati character set the generator produces SVGs for.

Every entry is a `Character`: the text as typed (one or more code points),
its category, and a romanisation used as a human-readable label in the
manifest.  Nothing here knows about fonts or SVGs.
"""

from dataclasses import dataclass

VIRAMA = "્"  # ્  - joins two consonants into a conjunct


@dataclass(frozen=True)
class Character:
    text: str
    category: str
    label: str

    @property
    def codepoints(self):
        return [ord(ch) for ch in self.text]

    @property
    def unicode(self):
        """Human form, e.g. 'U+0A95 U+0ABE'."""
        return " ".join(f"U+{cp:04X}" for cp in self.codepoints)

    @property
    def slug(self):
        """ASCII-safe file stem, e.g. 'u0A95_u0ABE'."""
        return "_".join(f"u{cp:04X}" for cp in self.codepoints)


# --- Vowels -----------------------------------------------------------------

_VOWELS = [
    ("અ", "a"),
    ("આ", "aa"),
    ("ઇ", "i"),
    ("ઈ", "ii"),
    ("ઉ", "u"),
    ("ઊ", "uu"),
    ("ઋ", "ru"),
    ("એ", "e"),
    ("ઐ", "ai"),
    ("ઓ", "o"),
    ("ઔ", "au"),
    ("અં", "am"),
    ("અઃ", "ah"),
]

# --- Consonants -------------------------------------------------------------

_CONSONANTS = [
    ("ક", "ka"), ("ખ", "kha"), ("ગ", "ga"), ("ઘ", "gha"), ("ઙ", "nga"),
    ("ચ", "cha"), ("છ", "chha"), ("જ", "ja"), ("ઝ", "jha"), ("ઞ", "nya"),
    # Retroflex row uses ITRANS capitals to stay ASCII-safe: Ta vs ta.
    ("ટ", "Ta"), ("ઠ", "Tha"), ("ડ", "Da"), ("ઢ", "Dha"), ("ણ", "Na"),
    ("ત", "ta"), ("થ", "tha"), ("દ", "da"), ("ધ", "dha"), ("ન", "na"),
    ("પ", "pa"), ("ફ", "pha"), ("બ", "ba"), ("ભ", "bha"), ("મ", "ma"),
    ("ય", "ya"), ("ર", "ra"), ("લ", "la"), ("વ", "va"),
    ("શ", "sha"), ("ષ", "Sha"), ("સ", "sa"), ("હ", "ha"),
    ("ળ", "La"),
]

# --- Conjuncts --------------------------------------------------------------

_COMBINED = [
    ("ક" + VIRAMA + "ષ", "ksha"),
    ("જ" + VIRAMA + "ઞ", "gnya"),
]

# --- Special forms ----------------------------------------------------------
# Clusters whose written shape is not just their parts side by side.  The four
# ra-conjuncts and રૂ each collapse into a single dedicated glyph in the font;
# ર્વ puts the ra on the roof as a reph.  All of it falls out of shaping - the
# entries are here because these forms are taught in their own right.

RA_VOCALIC = "ૃ"  # ૃ  - the vocalic-r matra, as in પૃ

_SPECIAL = [
    ("પ" + RA_VOCALIC, "pru"),          # પૃ  pa + vocalic r
    ("ર" + VIRAMA + "વ", "rva"),        # ર્વ reph over વ
    ("પ" + VIRAMA + "ર", "pra"),        # પ્ર
    ("ક" + VIRAMA + "ર", "kra"),        # ક્ર
    ("શ" + VIRAMA + "ર", "shra"),       # શ્ર
    ("ત" + VIRAMA + "ર", "tra"),        # ત્ર
    ("ર" + "ૂ", "ruu"),                 # રૂ  irregular ra + uu form
]

# --- Matras -----------------------------------------------------------------
# Each is (mark, suffix).  Used twice: as standalone cards, and to build the
# barakhadi, where the consonant's trailing "a" is replaced by the suffix -
# so ક ("ka") + ા  ->  "kaa".

MATRAS = [
    ("ા", "aa"),   # ા
    ("િ", "i"),    # િ
    ("ી", "ii"),   # ી
    ("ુ", "u"),    # ુ
    ("ૂ", "uu"),   # ૂ
    ("ે", "e"),    # ે
    ("ૈ", "ai"),   # ૈ
    ("ો", "o"),    # ો
    ("ૌ", "au"),   # ૌ
    ("ં", "am"),   # ં  anusvara
    ("ઃ", "ah"),   # ઃ  visarga
]


def _build(pairs, category):
    return [Character(text, category, label) for text, label in pairs]


VOWELS = _build(_VOWELS, "vowel")
CONSONANTS = _build(_CONSONANTS, "consonant")
COMBINED = _build(_COMBINED, "combined")
SPECIAL = _build(_SPECIAL, "special")
# The same 11 marks, twice: drawn bare, and drawn on a dotted circle.  Same
# text and so the same filename, kept apart by their category's folder.
MATRA_SIGNS = _build(MATRAS, "matra")
MATRA_CIRCLE_SIGNS = _build(MATRAS, "matra_circle")

BASE_CHARACTERS = VOWELS + CONSONANTS + COMBINED + SPECIAL


def barakhadi():
    """Every consonant crossed with every matra - 34 x 11 = 374 syllables."""
    rows = []
    for consonant in CONSONANTS:
        stem = consonant.label[:-1] if consonant.label.endswith("a") else consonant.label
        for mark, suffix in MATRAS:
            rows.append(
                Character(consonant.text + mark, "barakhadi", stem + suffix)
            )
    return rows


def all_characters(include_barakhadi=False, matra_style="both"):
    chars = list(BASE_CHARACTERS)
    if matra_style in ("bare", "both"):
        chars += MATRA_SIGNS
    if matra_style in ("circle", "both"):
        chars += MATRA_CIRCLE_SIGNS
    if include_barakhadi:
        chars += barakhadi()
    return chars
