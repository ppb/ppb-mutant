#!/usr/bin/env python3
"""
Show an index of available emoji
"""
import ppb
import os.path
import math
from ppb_mutant import MutantSprite, load_index
import pathlib


class Region(ppb.BaseSprite):
    @staticmethod
    def get_vector(other):
        if isinstance(other, ppb.BaseSprite):
            return other.position
        else:
            return other

    def contains(self, other):
        pos = self.get_vector(other)
        return (
            self.left <= pos.x <= self.right
            and
            self.bottom >= pos.y >= self.top
        )


class EmojiSprite(MutantSprite, Region):
    def __init__(self, *p, emoji, **kw):
        super().__init__(*p, **kw)
        self.emoji = emoji

    def on_button_pressed(self, mouse, signal):
        if self.contains(mouse.position):
            print(self.emoji)

    resource_path = pathlib.Path('.')


class IndexScene(ppb.BaseScene):
    def __init__(self, *p, **kw):
        super().__init__(*p, pixel_ratio=64, **kw)

        for s in self.get_options():
            self.add(s)

    def _load_index(self):
        with open('mutant/index.txt', 'rt') as indexfile:
            for line in indexfile:
                yield line.strip()

    def grid(self, rows, cols, *, scale=1.0):
        for y in range(rows):
            for x in range(cols):
                yield x * scale, y * scale

    def compile_emojis(self):
        # Load the index
        index = sorted(load_index(), key=lambda v: v[1])
        # Reduce to aliases, removing duplicates
        emojis = []
        for shortcode, path, alias in index:
            name = alias or shortcode
            if name not in emojis:
                emojis.append(name)
        return emojis[:256]

    def get_options(self):
        emojis = self.compile_emojis()
        cols = math.floor(math.sqrt(len(emojis)))
        rows = math.ceil(len(emojis) / cols)
        for emoji, pos in zip(emojis, self.grid(rows, cols, scale=1.1)):
            yield EmojiSprite(emoji=emoji, pos=pos)
        print(f"Loaded {len(emojis)} emoji")
        

if __name__ == '__main__':
    ppb.run(IndexScene,
        window_title='Mutant Standard Index',
    )
