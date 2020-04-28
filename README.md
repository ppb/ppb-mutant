ppb-mutant
==========

This library provides convenient support for the [Mutant Standard emoji](https://mutant.tech) for games using the [PursuedPyBear engine](https://ppb.dev/).

This version is for PursuedPyBear v0.8 and Mutant Standard v2020.04.


Setup
=====
1. Install the `ppb-mutant` package through your preferred package management
   system. (pip, `requirements.txt`, pipenv, poetry, etc)


Usage
=====

Demo
----

A demo showing all emoji can be found by running `python -m ppb_mutant.index`.


`Emoji`
-------

You can replace the use of `image` with an `Emoji` asset:

```python
class SlimeSprite(ppb.Sprite):
    image = ppb_mutant.Emoji('slime')
```

In addition, the formatting syntax with the variables `morph` and `skin` may be
used for Mutant's customization features:

```python
class PunchRightSprite(ppb.Sprite):
    image = ppb_mutant.Emoji('fist_facing_right_{morph}_{skin}', morph='clw', tone='r2')
```

See the [modifier guide](https://mutant.tech/reference/0.3.0/mutstd_modifier_guide_0.3.0.png) for details on these.

Alternatively, most customizable emoji also have aliases defined:

```python
class PunchRightSprite(ppb.Sprite):
    image = ppb_mutant.Emoji('fist_facing_right', morph='clw', tone='r2')
```

`MorphToneGroup`
----------------

If you want to change the morph/tone of a bunch of emoji as a group, use the `MorphToneGroup`:

```python
player_emoji = ppb_mutant.MorphToneGroup(morph='paw', tone='g1')


class HandSprite(ppb.Sprite):
    image = player_emoji('hand')


class ProfileSprite(ppb.Sprite):
    image = player_emoji('adult')
```


`SelectScene`
-------------

`SelectScene` is a base for  allowing you to handle mutant morph and tone
(color) customization. It can be used like:

```python
class CustomizeScene(ppb_mutant.SelectScene):
    class Sprite(ppb_mutant.SelectScene.Sprite): pass

    class BackSprite(Region, ppb.Sprite):
        image = Emoji('tick')
        def on_button_pressed(self, mouse, signal):
            if self.contains(mouse.position) and mouse.button is ppb.buttons.Primary:
                signal(ppb.events.StopScene())

    def __init__(self, **props):
        super().__init__(**props)
        self.add(self.BackSprite(position=(-4, 1.5)))

    def do_update_morphtone(self):
        print(self.morph, self.tone)
```

For a demo, run `python -m ppb_mutant.picker`.


Copyright Notice
================

This library uses [Mutant Standard emoji](https://mutant.tech), which are licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).


Development
===========
The image assets are not stored in git.

You can download a copy from the mutant standard website by running `build.sh`.
