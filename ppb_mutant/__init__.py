import ppb
from ppb.flags import DoNotRender

# The BY-NC-SA license requires software display this notice. Let's just do it
# for them.
print(
    "This game uses Mutant Standard emoji (https://mutant.tech), which are "
    "licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
    "International License (https://creativecommons.org/licenses/by-nc-sa/4.0/)."
)


class MutantSprite(ppb.BaseSprite):
    kind = 'hmn'
    color = 'h5'
    emoji = 'symbols/restrictive/no_entry'

    @property
    def image(self):
        if self.emoji is DoNotRender:
            return DoNotRender
        else:
            return 'mutant/{}.png'.format(
                self.emoji.format(kind=self.kind, color=self.color)
            )
