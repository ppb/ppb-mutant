ppb-mutant
==========

This library provides convenient support for the [Mutant Standard emoji](https://mutant.tech) for games using the [PusuedPyBear engine](https://github.com/ppb/pursuedpybear).

Setup
=====
1. Install the `ppb-mutant` package through your preferred package management
   system. (pip, `requirements.txt`, pipenv, poetry, etc)
2. Run `python -m ppb_mutant.download` in your project to download the Mutant
   Standard assets (specifically, the 64px versions)

Usage
=====

`MutantSprite`
--------------

You can replace the use of `image` in your sprites with `emoji` like so:

```python
class SlimeSprite(ppb_mutant.MutantSprite):
    emoji = 'people_animals/creatures/other/slime'
```

In addition, the formatting syntax with the variables `kind` and `skin` may be
used for Mutant's customization features:

```python
class PunchRightSprite(ppb_mutant.MutantSprite):
    emoji = 'expressions/hands/{kind}/fist_facing_right_{kind}_{skin}'
    morph = 'clw'
    tone = 'r2'  # "colour"
```

See the [modifier guide](https://github.com/astronouth7303/ppb-mutant/blob/master/modifier-guide.png) for details on these.


Copyright Notice
================

This library uses [Mutant Standard emoji](https://mutant.tech), which are licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
