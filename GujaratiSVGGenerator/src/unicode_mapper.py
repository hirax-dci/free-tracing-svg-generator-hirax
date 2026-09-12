class UnicodeMapper:

    def __init__(self, font):
        self.cmap = font.getBestCmap()

    def glyph_name(self, character):
        codepoint = ord(character)

        glyph = self.cmap.get(codepoint)

        if glyph is None:
            raise ValueError(f"No glyph found for {character}")

        return glyph