"""
Tools for using Mutant Standard emoji from ppb games.

Constants:
* MORPHS: Valid morph values
* TONES: Valid tone values
* TONES_HMN, TONES_PAW, TONES_CLW: Valid tone values for specific morphs
* TONES_ALL: Valid tone values for all morphs
"""
import ppb
from ppb.flags import DoNotRender
import weakref
import logging
import functools

__all__ = (
    'Emoji', 'MorphToneGroup', 'SelectScene',
    # Deprecated
    'MutantSprite',
)

# The BY-NC-SA license requires software display this notice. Let's just do it
# for them.
print(
    "\n"
    "This game uses Mutant Standard emoji (https://mutant.tech), which are "
    "licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
    "International License (https://creativecommons.org/licenses/by-nc-sa/4.0/)."
    "\n"
)

logger = logging.getLogger(__name__)


# Be sure to update these in download_zips.py
MORPHS = ['hmn', 'paw', 'clw', 'hoof']

TONES_ALL = [
    None,  # Same as k2
    # Standard
    'r1', 'r2', 'r3', 'd1', 'd2', 'd3', 'o1', 'o2', 'o3', 'y1', 'y2', 'y3',
    'l1', 'l2', 'l3', 'g1', 'g2', 'g3', 't1', 't2', 't3', 'c1', 'c2', 'c3',
    's1', 's2', 's3', 'b1', 'b2', 'b3', 'v1', 'v2', 'v3', 'm1', 'm2', 'm3',
    'p1', 'p2', 'p3', 'e1', 'e2', 'e3', 'k1', 'k2', 'k3',
]

TONES_HMN = ['h1', 'h2', 'h3', 'h4', 'h5']
TONES_PAW = ['fk1', 'ft1', 'fe1']
TONES_CLW = []
TONES_HOOF = []

TONES = TONES_ALL + TONES_HMN + TONES_PAW + TONES_CLW + TONES_HOOF


@functools.lru_cache()
def load_index():
    """
    Loads the index file, yielding (shortcode, original path, alias)
    """
    rv = []
    try:
        with ppb.vfs.open('ppb_mutant/_assets/index.txt', encoding='utf-8') as indexfile:
            for line in indexfile:
                line = line.rstrip('\n')
                if not line:
                    continue
                bits = line.split('\t')
                code, path, alias = bits
                rv.append((code, path, alias or None))
    except FileNotFoundError:
        pass
    return rv


@functools.lru_cache()
def load_aliases():
    """
    Loads the aliases file, yielding (alias, expansion)
    """
    rv = {}
    try:
        with ppb.vfs.open('ppb_mutant/_assets/aliases.txt', encoding='utf-8') as indexfile:
            for line in indexfile:
                line = line.strip()
                if not line:
                    continue
                bits = line.split('\t')
                alias, expansion = bits
                rv[alias] = expansion
    except FileNotFoundError:
        pass
    return rv


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
    if morph == 'hoof' and tone in TONES_HOOF:
        return True

    # Fall through
    return False


def _resolve_name(shortcode, morph, tone):
    if shortcode == 'color_modifier' and tone is None:
        # color_modifier doesn't ship with a None tone, but None == k2
        tone = 'k2'
    elif shortcode == 'hand_splayed' and morph == 'paw':
        # paw's :hand: is already splayed
        shortcode = 'hand'
    aliases = load_aliases()

    resolved = aliases.get(shortcode, shortcode)
    resolved = resolved.format(morph=morph, tone=tone or '')
    resolved = resolved.rstrip('_')
    return 'ppb_mutant/_assets/{}.png'.format(resolved)


class Emoji(ppb.Image):
    def __new__(cls, shortcode, *, morph='hmn', tone=None):
        return super().__new__(cls, _resolve_name(shortcode, morph, tone))

    def __init__(self, shortcode, *, morph='hmn', tone=None):
        self.shortcode = shortcode
        self.morph = morph
        self.tone = tone

        super().__init__(_resolve_name(self.shortcode, self.morph, self.tone))

    def __repr__(self):
        return f"<{type(self).__name__} shortcode={self.shortcode!r} morph={self.morph!r} tone={self.tone!r} name={self.name!r}>"


class MorphToneProxy:
    """
    A proxy for Emoji used with MorphToneGroup.

    Use MorphToneGroup to construct.
    """
    _image = None

    def __init__(self, shortcode, group):
        self.shortcode = shortcode
        self._group = group
        self._reload()

    def __repr__(self):
        return f"<{type(self).__name__} shortcode={self.shortcode!r} group={self._group!r}>"

    @property
    def morph(self):
        return self._group.morph

    @property
    def tone(self):
        return self._group.tone

    def _reload(self):
        if self.shortcode in load_aliases() or self._image is None:
            self._image = Emoji(self.shortcode, morph=self.morph, tone=self.tone)

    def load(self):
        if self._image is None:
            self._reload()
        return self._image.load()


class MorphToneGroup:
    """
    A group of emoji that share a changable morph/tone.
    """
    def __init__(self, *, morph='hmn', tone=None):
        self._emoji = weakref.WeakValueDictionary()
        self._morph = morph
        self._tone = tone

    @property
    def morph(self):
        return self._morph

    @morph.setter
    def morph(self, value):
        self._morph = value
        self._reload()

    @property
    def tone(self):
        return self._tone

    @tone.setter
    def tone(self, value):
        self._tone = value
        self._reload()

    def set_morphtone(self, morph, tone):
        self._morph = morph
        self._tone = tone
        self._reload()

    def _reload(self):
        for emoji in list(self._emoji.values()):
            emoji._reload()

    def __call__(self, shortcode):
        """
        Get an emoji asset
        """
        # We do things in this particular way to avoid race conditions around the gc
        try:
            return self._emoji[shortcode]
        except KeyError:
            e = MorphToneProxy(shortcode, self)
            self._emoji[shortcode] = e
            return e


class MutantSprite(ppb.BaseSprite):
    """
    Deprecated
    """
    morph = 'hmn'
    tone = None
    emoji = 'no_entry'

    _image = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        logger.warn("MutantSprite is deprecated. Use the Emoji or MorphToneGroup instead (in %s)", cls.__name__)

    @property
    def image(self):
        if self.emoji is DoNotRender:
            return DoNotRender
        else:
            emoji = self.emoji.rsplit('/', 1)[-1]
            if self._image is None or (
                self._image.shortcode != emoji or
                self._image.morph != self.morph or
                self._image.tone != self.tone
            ):
                self._image = Emoji(emoji, morph=self.morph, tone=self.tone)
            return self._image


def _frange(x, y, jump):
    if jump > 0:
        while x <= y:
            yield x
            x += jump
    else:
        while x >= y:
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

    #: Hoof hands have incomplete emoji coverage, so games may choose to opt-out of it.
    include_hoof = True

    class Sprite(ppb.BaseSprite):
        """
        The sprite to use in the menu
        """

    def __init__(self, *p, morph='hmn', tone=None, mtg=None, **kw):
        if mtg is None:
            mtg = MorphToneGroup(morph=morph, tone=tone)
        super().__init__(*p, mtg=mtg, **kw)

        self.main_camera.position = ppb.Vector(
            0,
            -self.main_camera.half_height + 2,
        )

        for s in self._get_samples():
            self.add(s, tags=['sample'])

        for s in self._get_morphs():
            self.add(s, tags=['morph'])

        for s in self._get_tones():
            self.add(s, tags=['tone'])

        # ymin = min(s.bottom - 0.5 for s in self)
        # ymax = max(s.top + 0.5 for s in self)

    def _get_samples(self):
        left = self.main_camera.frame_left
        yield self.Sprite(image=self.mtg('hand'), pos=(left + 0.5, 1.5))
        yield self.Sprite(image=self.mtg('raising_hand'), pos=(left + 1.5, 1.5))

    def _get_morphs(self):
        right = self.main_camera.frame_right
        yield self.Sprite(image=Emoji('hand', morph='clw', tone=None), pos=(right - 0.5, 1.5))
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone=None), pos=(right - 1.5, 1.5))
        yield self.Sprite(image=Emoji('hand', morph='paw', tone=None), pos=(right - 2.5, 1.5))
        if self.include_hoof:
            yield self.Sprite(image=Emoji('hand', morph='hoof', tone=None), pos=(right - 3.5, 1.5))

    def _grid(self):
        cam = self.main_camera

        for y in _frange(-1, -int(cam.frame_height - 2) + 0.5, -1.0):
            for x in _frange(int(cam.frame_left) + 0.5, int(cam.frame_right) - 0.5, 1.0):
                yield x, y

    def _get_tones(self):
        left = self.main_camera.frame_left
        right = self.main_camera.frame_right

        # TONES_HMN
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone='h1'), pos=(left + 0.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone='h2'), pos=(left + 1.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone='h3'), pos=(left + 2.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone='h4'), pos=(left + 3.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='hmn', tone='h5'), pos=(left + 4.5, 0))

        # Default tone
        # yield self.Sprite(image=Emoji('cross'), pos=((left + 4.5 + right - 2.5) / 2, 0))
        yield self.Sprite(image=Emoji('cross'), pos=(0, 0))

        # TONES_PAW
        yield self.Sprite(image=Emoji('hand', morph='paw', tone='fk1'), pos=(right - 0.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='paw', tone='ft1'), pos=(right - 1.5, 0))
        yield self.Sprite(image=Emoji('hand', morph='paw', tone='fe1'), pos=(right - 2.5, 0))

        # TONES_ALL
        tones = (t for t in TONES_ALL if t is not None)
        for tone, pos in zip(tones, self._grid()):
            yield self.Sprite(image=Emoji('color_modifier', tone=tone), pos=pos)

    @property
    def morph(self):
        """
        The currently selected morph
        """
        return self.mtg.morph

    @morph.setter
    def morph(self, value):
        self.mtg.morph = value
        self.do_update_morphtone()

    @property
    def tone(self):
        """
        The currently selected tone
        """
        return self.mtg.tone

    @tone.setter
    def tone(self, value):
        self.mtg.tone = value
        self.do_update_morphtone()

    def _check_collision(self, sprite, point):
        return (
            sprite.left <= point.x <= sprite.right
            and
            sprite.bottom <= point.y <= sprite.top
        )

    def on_button_pressed(self, mouse, signal):
        for sprite in self.get(tag='morph'):
            if self._check_collision(sprite, mouse.position):
                if not is_valid_morph_tone(sprite.image.morph, self.tone):
                    self.tone = None
                self.morph = sprite.image.morph
                return

        for sprite in self.get(tag='tone'):
            if self._check_collision(sprite, mouse.position):
                if not is_valid_morph_tone(self.morph, sprite.image.tone):
                    if sprite.image.tone in TONES_PAW:
                        self.morph = 'paw'
                    elif sprite.image.tone in TONES_HMN:
                        self.morph = 'hmn'
                    elif sprite.image.tone in TONES_CLW:
                        self.morph = 'clw'
                self.tone = sprite.image.tone
                return

    def do_update_morphtone(self):
        """
        Called whenever the morph or tone is updated. Override with your own class.
        """
