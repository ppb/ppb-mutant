#!/usr/bin/env python3
"""
Show the morph/tone picker.
"""
import ppb
from ppb_mutant import SelectScene


class SelectDemoScene(SelectScene):
    def do_update_morphtone(self):
        print(self.morph, self.tone)


if __name__ == '__main__':
    ppb.run(
        starting_scene=SelectDemoScene,
        # window_title='Mutant Morph/Tone Picker',
    )
