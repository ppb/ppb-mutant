#!/usr/bin/env python3
"""
Show an index of available emoji
"""
import ppb
import os.path
import math
from ppb_mutant import MutantSprite, load_index
import pathlib
from time import perf_counter


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
            self.add(s, tags=['emoji'])

        self.xmin = min(s.position.x - 0.5 for s in self.get(tag='emoji'))
        self.xmax = max(s.position.x + 0.5 for s in self.get(tag='emoji'))
        self.ymin = min(s.position.y - 0.5  for s in self.get(tag='emoji'))
        self.ymax = max(s.position.y + 0.5 for s in self.get(tag='emoji'))

        self.main_camera.position = ppb.Vector(
            (self.xmin + self.xmax) / 2,
            (self.ymin + self.ymax) / 2,
        )

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
        return emojis

    def get_options(self):
        emojis = self.compile_emojis()
        cols = math.floor(math.sqrt(len(emojis)))
        rows = math.ceil(len(emojis) / cols)
        for emoji, pos in zip(emojis, self.grid(rows, cols, scale=1.1)):
            yield EmojiSprite(emoji=emoji, pos=pos)
        print(f"Loaded {len(emojis)} emoji")

    def on_update(self, event, signal):
        cam = self.main_camera
        # https://github.com/ppb/pursuedpybear/issues/135
        cam.frame_width = cam.viewport_width / cam.pixel_ratio
        cam.frame_height = cam.viewport_height / cam.pixel_ratio
        cam.half_width = cam.frame_width / 2
        cam.half_height = cam.frame_height / 2

    frame_happened = False
    
    def on_mouse_motion(self, mouse, signal):
        if not self.frame_happened:
            return
        self.frame_happened = False
        print("mouse", mouse.position)
        x, y = mouse.position
        cam = self.main_camera

        if not (cam.frame_width and cam.frame_height):
            return

        frame_left, frame_right, frame_top, frame_bottom = \
            cam.frame_left, cam.frame_right, cam.frame_top, cam.frame_bottom

        frame_width, frame_height = cam.frame_width, cam.frame_height

        # if not (self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax):
        #     return

        print("cam.x", frame_left, frame_width, frame_right)
        print("cam.y", frame_top, frame_height, frame_bottom)
        xpercent = (x - frame_left) / frame_width
        ypercent = (y - frame_top) / frame_height

        print("x", self.xmin, "->", self.xmax, "\t", xpercent)
        print("y", self.ymin, "->", self.ymax, "\t", ypercent)

        if xpercent < 0: xpercent = 0
        if xpercent > 1: xpercent = 1
        if ypercent < 0: ypercent = 0
        if ypercent > 1: ypercent = 1

        dest = ppb.Vector(
            (self.xmax - self.xmin) * xpercent + self.xmin,
            (self.ymax - self.ymin) * ypercent + self.ymin,
        )
        print("->", dest)

        cam.position = dest

    last_frame = None
    def on_pre_render(self, event, signal):
        self.frame_happened = True


if __name__ == '__main__':
    ppb.run(IndexScene,
        window_title='Mutant Standard Index',
    )
