import pathlib
import json
import ppb_mutant
from download_zips import AliasCompiler

assetsdir = pathlib.Path(ppb_mutant.__file__).absolute().parent / '_assets'
rootdir = pathlib.Path(__file__).absolute().parent


with open(rootdir / 'struct.json', 'rt') as f:
    data = json.load(f)

aliases = AliasCompiler()

# {
#     "cat": "expressions",
#     "code": "hand_splayed_hmn_r1",
#     "color": "r1",
#     "morph": "hmn",
#     "root": "hand_splayed",
#     "src": "expressions/hands/hmn/hand_splayed [hmn].svg",
#     "unicode": [
#         128400,
#         65039,
#         1054208
#     ]
# }

for emoji in data:
    shortcode = emoji['short']
    src = pathlib.Path(emoji['src'])

    path = src.parent / (shortcode + '.png')
    if 'morph' in emoji:
        expansion = 2
    elif 'color' in emoji:
        expansion = 1
    else:
        expansion = None

    if expansion:
        alias = emoji['root']
        if alias == '!undefined':
            # Modifiers
            alias = src.stem
    else:
        alias = None

    aliases.add_path(path, alias=alias, expansion=expansion)

with open(assetsdir / "index.txt", 'at') as indexfile:
    aliases.write_code_index(indexfile)

with open(assetsdir / "aliases.txt", 'at') as indexfile:
    aliases.write_alias_index(indexfile)
