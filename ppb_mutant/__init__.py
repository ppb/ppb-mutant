"""
Tools for using Mutant Standard emoji from ppb games.

Constants:
* MORPHS: Valid morph values
* TONES: Valid tone values
* TONES_HMN, TONES_PAW, TONES_CLW: Valid tone values for specific morphs
* TONES_ALL: Valid tone values for all morphs
"""
from typing import Iterable, Tuple, Optional
import ppb
from ppb.flags import DoNotRender
import os
import functools

__all__ = 'MutantSprite', 'SelectScene',

# The BY-NC-SA license requires software display this notice. Let's just do it
# for them.
print(
    "\n"
    "This game uses Mutant Standard emoji (https://mutant.tech), which are "
    "licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
    "International License (https://creativecommons.org/licenses/by-nc-sa/4.0/)."
    "\n"
)


MORPHS = ['hmn', 'paw', 'clw']

TONES_ALL = [
    None,
    # Standard
    'r1', 'r2', 'r3', 'd1', 'd2', 'd3', 'o1', 'o2', 'o3', 'y1', 'y2', 'y3',
    'l1', 'l2', 'l3', 'g1', 'g2', 'g3', 't1', 't2', 't3', 'c1', 'c2', 'c3',
    's1', 's2', 's3', 'b1', 'b2', 'b3', 'v1', 'v2', 'v3', 'm1', 'm2', 'm3',
    'p1', 'p2', 'p3', 'e1', 'e2', 'e3', 'k1', 'k2', 'k3',
]

TONES_HMN = ['h1', 'h2', 'h3', 'h4', 'h5']
TONES_PAW = ['fk1', 'ft1', 'fe1']
TONES_CLW = []

TONES = TONES_ALL + TONES_HMN + TONES_PAW + TONES_CLW


@functools.lru_cache()
def load_index() -> Iterable[Tuple[str, str, Optional[str]]]:
    """
    Loads the index file, yielding (shortcode, original path, alias)
    """
    if not os.path.exists('mutant/index.txt'):
        # Does not exist yet
        return
    with open('mutant/index.txt', 'rt') as indexfile:
        for line in indexfile:
            line = line.rstrip('\n')
            if not line:
                continue
            bits = line.split('\t')
            code, path, alias = bits
            yield code, path, alias or None


@functools.lru_cache()
def load_aliases() -> Iterable[Tuple[str, str]]:
    """
    Loads the aliases file, yielding (shortcode, original path, alias)
    """
    if not os.path.exists('mutant/aliases.txt'):
        # Does not exist yet
        return
    with open('mutant/aliases.txt', 'rt') as indexfile:
        for line in indexfile:
            line = line.strip()
            if not line:
                continue
            bits = line.split('\t')
            alias, expansion = bits
            yield alias, expansion


def is_valid_morph_tone(morph, tone):
    """
    Returns True if this is a valid morph, a valid tone, and they are valid
    together.
    """
    if morph not in MORPHS:
        return False
    if tone in TONES_ALL:
        return True
    if morph == 'hmn' and tone in TONES_HMN:
        return True
    if morph == 'paw' and tone in TONES_PAW:
        return True
    if morph == 'clw' and tone in TONES_CLW:
        return True

    # Fall through
    return False


class MutantSprite(ppb.BaseSprite):
    """
    Replaces a Sprite's image with emoji, which is pulled from the Mutant
    Standard emoji.

    Morph and tone customization can be used via {}-format.

    Attributes (can be set at the class level):
    * emoji: the emoji to render
    * morph: the hand shape to use (hmn, paw, or clw)
    * tone: the tone to color with
    """
    morph: str = 'hmn'
    tone: typing.Optional[str] = None
    emoji: typing.Union[str, typing.Type[DoNotRender]] = 'no_entry'

    _aliases = dict(load_aliases())

    @property
    def image(self) -> str:
        if self.emoji is DoNotRender:
            return DoNotRender
        else:
            shortcode = os.path.basename(self.emoji)  # Transitional
            resolved = self._aliases.get(shortcode, shortcode)
            resolved = resolved.format(morph=self.morph, tone=self.tone or '')
            resolved = resolved.rstrip('_')
            return 'mutant/{}.png'.format(resolved)


def _frange(x, y, jump):
  while x <= y:
    yield x
    x += jump


class SelectScene(ppb.BaseScene):
    """
    A base scene to provide mutant hand/character customization.

    Subclass and override do_morphtone().

    * morph: The current morph
    * tone: The current color tone
    * do_morphtone(): Called whenever the morph or tone changes

    SelectScene.Sprite can be overriden to change the sprite.
    """
    _morph = None
    _tone = None
    
    class Sprite(MutantSprite):
        """
        The sprite to use in the menu
        """

    def __init__(self, *p, morph='hmn', tone=None, **kw):
        super().__init__(*p, **kw)

        self.main_camera.position = ppb.Vector(
            0,
            self.main_camera.half_height - 2,
        )

        for s in self._get_samples():
            self.add(s, tags=['sample'])

        for s in self._get_morphs():
            self.add(s, tags=['morph'])

        for s in self._get_tones():
            self.add(s, tags=['tone'])

        self.morph = morph
        self.tone = tone

        ymin = min(s.position.y - 0.5 for s in self)
        ymax = max(s.position.y + 0.5 for s in self)

    def build_sprite(self, emoji, morph=None, tone=None, **kwargs):
        """
        Instantiates the sprite, with the given emoji, morph, tone, and args.
        """
        sprite = self.Sprite(**kwargs)
        sprite.emoji = emoji
        if morph:
            sprite.morph = morph
        if tone:
            sprite.tone = tone
        return sprite

    def _get_samples(self):
        left = self.main_camera.frame_left
        yield self.build_sprite(emoji='hand', pos=(left + 0.5, -1.5))
        yield self.build_sprite(emoji='raising_hand', pos=(left + 1.5, -1.5))

    def _get_morphs(self):
        right = self.main_camera.frame_right
        yield self.build_sprite(emoji='hand', morph='clw', tone=None, pos=(right - 0.5, -1.5))
        yield self.build_sprite(emoji='hand', morph='hmn', tone=None, pos=(right - 1.5, -1.5))
        yield self.build_sprite(emoji='hand', morph='paw', tone=None, pos=(right - 2.5, -1.5))

    def _grid(self):
        cam = self.main_camera
        
        for y in _frange(1, int(cam.frame_height - 2) - 0.5, 1.0):
            for x in _frange(int(cam.frame_left) + 0.5, int(cam.frame_right) - 0.5, 1.0):
                yield x, y

    def _get_tones(self):
        left = self.main_camera.frame_left
        right = self.main_camera.frame_right

        # TONES_HMN
        yield self.build_sprite(emoji='color_modifier', tone='h1', pos=(left + 0.5, 0))
        yield self.build_sprite(emoji='color_modifier', tone='h2', pos=(left + 1.5, 0))
        yield self.build_sprite(emoji='color_modifier', tone='h3', pos=(left + 2.5, 0))
        yield self.build_sprite(emoji='color_modifier', tone='h4', pos=(left + 3.5, 0))
        yield self.build_sprite(emoji='color_modifier', tone='h5', pos=(left + 4.5, 0))

        yield self.build_sprite(emoji='color_modifier', tone=None, pos=((left + 4.5 + right - 2.5) / 2, 0))

        # TONES_PAW
        # FIXME: Use color_modifier when available for these tones
        yield self.build_sprite(emoji='hand_paw_{tone}', tone='fk1', pos=(right - 0.5, 0))
        yield self.build_sprite(emoji='hand_paw_{tone}', tone='ft1', pos=(right - 1.5, 0))
        yield self.build_sprite(emoji='hand_paw_{tone}', tone='fe1', pos=(right - 2.5, 0))

        # TONES_ALL
        tones = (t for t in TONES_ALL if t is not None)
        for tone, pos in zip(tones, self._grid()):
            yield self.build_sprite(emoji='color_modifier', tone=tone, pos=pos)

    @property
    def morph(self):
        return self._morph

    @morph.setter
    def morph(self, value):
        self._morph = value
        for s in self.get(tag='sample'):
            s.morph = value
        self.do_update_morphtone()

    @property
    def tone(self):
        return self._tone

    @tone.setter
    def tone(self, value):
        self._tone = value
        for s in self.get(tag='sample'):
            s.tone = value
        self.do_update_morphtone()

    def _check_collision(self, sprite, point):
        return (
            sprite.left <= point.x <= sprite.right
            and
            sprite.bottom >= point.y >= sprite.top
        )

    def on_button_pressed(self, mouse, signal):
        for sprite in self.get(tag='morph'):
            if self._check_collision(sprite, mouse.position):
                if not is_valid_morph_tone(sprite.morph, self.tone):
                    self.tone = None
                self.morph = sprite.morph
                return

        for sprite in self.get(tag='tone'):
            if self._check_collision(sprite, mouse.position):
                if is_valid_morph_tone(self.morph, sprite.tone):
                    self.tone = sprite.tone
                return

    def do_update_morphtone(self):
        """
        Called whenever the morph or tone is updated. Override with your own class.
        """
