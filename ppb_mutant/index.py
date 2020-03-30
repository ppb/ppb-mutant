#!/usr/bin/env python3
"""
Show an index of available emoji
"""
import ppb
from ppb.features.loadingscene import BaseLoadingScene
import math
from ppb_mutant import Emoji, MorphToneGroup, load_index, SelectScene


class LoadingScene(BaseLoadingScene):
    background_color = 0, 0, 0
    loading_icon = Emoji('thinking')
    rotation_rate = 5 / 360  # 5s/full rotation

    def __init__(self, **props):
        super().__init__(**props)
        self.spinner = ppb.Sprite(image=self.loading_icon, size=4)
        self.add(self.spinner)

    def on_update(self, event, signal):
        self.spinner.rotation += self.rotation_rate * event.time_delta


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
            self.bottom <= pos.y <= self.top
        )


class EmojiSprite(Region, ppb.BaseSprite):
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)

    def on_button_pressed(self, mouse, signal):
        if self.contains(mouse.position):
            print(self.image.shortcode)


class OpenMenuSprite(Region, ppb.BaseSprite):
    image = Emoji('color_modifier')

    def on_button_pressed(self, mouse, signal):
        if self.contains(mouse.position) and mouse.button is ppb.buttons.Primary:
            signal(ppb.events.StartScene(
                CustomizeScene(mtg=mouse.scene._mtg)
            ))

    def on_pre_render(self, event, signal):
        cam = event.scene.main_camera
        self.position = ppb.Vector(cam.frame_left + 0.5, cam.frame_top - 0.5)


class IndexScene(ppb.BaseScene):
    def __init__(self, *p, **kw):
        super().__init__(*p, pixel_ratio=64, **kw)

        self._mtg = MorphToneGroup()

        for s in self.get_options():
            self.add(s, tags=['emoji'])

        self.add(OpenMenuSprite())

        self.xmin = min(s.left for s in self.get(tag='emoji'))
        self.xmax = max(s.right for s in self.get(tag='emoji'))
        self.ymin = min(s.bottom for s in self.get(tag='emoji'))
        self.ymax = max(s.top for s in self.get(tag='emoji'))

        self.main_camera.position = ppb.Vector(
            (self.xmin + self.xmax) / 2,
            (self.ymin + self.ymax) / 2,
        )

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
            yield EmojiSprite(image=self._mtg(emoji), pos=pos)
        print(f"Loaded {len(emojis)} emoji")

    frame_happened = False

    def on_pre_render(self, event, signal):
        self.frame_happened = True

    def on_mouse_motion(self, mouse, signal):
        if not self.frame_happened:
            return
        self.frame_happened = False
        x, y = mouse.position
        cam = self.main_camera

        if not (cam.frame_width and cam.frame_height):
            return

        frame_left, frame_right, frame_top, frame_bottom = \
            cam.frame_left, cam.frame_right, cam.frame_top, cam.frame_bottom

        frame_width, frame_height = cam.frame_width, cam.frame_height

        # if not (self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax):
        #     return

        xpercent = (x - frame_left) / frame_width
        ypercent = (y - frame_bottom) / frame_height

        if xpercent < 0: xpercent = 0
        if xpercent > 1: xpercent = 1
        if ypercent < 0: ypercent = 0
        if ypercent > 1: ypercent = 1

        cam.position = ppb.Vector(
            (self.xmax - self.xmin) * xpercent + self.xmin,
            (self.ymax - self.ymin) * ypercent + self.ymin,
        )


class CustomizeScene(SelectScene):
    class BackSprite(Region, SelectScene.Sprite):
        image = Emoji('tick')

        def on_button_pressed(self, mouse, signal):
            if self.contains(mouse.position) and mouse.button is ppb.buttons.Primary:
                signal(ppb.events.StopScene())

    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)
        self.add(self.BackSprite(
            pos=ppb.Vector(0, self.main_camera.frame_top - 0.5)
        ))


if __name__ == '__main__':
    ppb.run(
        starting_scene=LoadingScene, scene_kwargs={'next_scene': IndexScene},
        title='Mutant Standard Index',
    )
