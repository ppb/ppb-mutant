from typing import Iterable, Tuple, Optional
import ppb
from ppb.flags import DoNotRender
import os
import functools

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
    # Standard
    'r1', 'r2', 'r3', 'd1', 'd2', 'd3', 'o1', 'o2', 'o3', 'y1', 'y2', 'y3',
    'l1', 'l2', 'l3', 'g1', 'g2', 'g3', 't1', 't2', 't3', 'c1', 'c2', 'c3',
    's1', 's2', 's3', 'b1', 'b2', 'b3', 'v1', 'v2', 'v3', 'm1', 'm2', 'm3',
    'p1', 'p2', 'p3', 'e1', 'e2', 'e3', 'k1', 'k2', 'k3',
]

TONES_HMN = ['h1', 'h2', 'h3', 'h4', 'h5']
TONES_PAW = ['fk1', 'ft1', 'fe1']
TONES_CLAW = []

TONES = TONES_ALL + TONES_HMN + TONES_PAW + TONES_CLAW


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
    Loads the index file, yielding (shortcode, original path, alias)
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


class MutantSprite(ppb.BaseSprite):
    morph = 'hmn'
    tone = None
    emoji = 'symbols/restrictive/no_entry'

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
