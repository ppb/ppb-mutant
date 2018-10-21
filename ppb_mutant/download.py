#!/usr/bin/env python3
import os
import sys
import urllib.request
import zipfile
import io
import argparse
import re
from ppb_mutant import MORPHS, TONES

DOWNLOADS = [
    ('https://mutant.tech/dl/0.3.0/mutstd_0.3.0_shortcode_png64.zip', 'mutstd_0.3.0_shortcode_png64/emoji/'),
    ('https://mutant.tech/dl/vip/mutstd_vip_2018.04_all.zip', 'mutstd_vip_2018.04_all/emoji/png-64px/'),
    ('https://mutant.tech/dl/special/mutstd_special_s1_all.zip', 'mutstd_special_s1_all/emoji/png-64px/'),
]

def parse_args():
    parser = argparse.ArgumentParser(
        description=
            'Download the Mutant Standard emoji to mutant/ in the current directory.',
    )

    return parser.parse_args()


def open_zip(url):
    with urllib.request.urlopen(url) as resp:
        return io.BytesIO(resp.read())

real_tones = [t for t in TONES if t is not None]

class AliasCompiler:
    MORPHTONE = re.compile(f"^(.*)_({'|'.join(MORPHS)})_({'|'.join(real_tones)})$")
    TONEONLY = re.compile(f"^(.*)_({'|'.join(real_tones)})$")
    MORPHONLY = re.compile(f"^(.*)_({'|'.join(MORPHS)})$")

    def __init__(self):
        self.codes = {}
        self.code2alias = {}
        self.aliases = {}

    def guess_alias(self, shortcode):
        m = self.MORPHTONE.match(shortcode)
        if m:
            name = m.group(1)
            return name, name + "_{morph}_{tone}"
        m = self.MORPHONLY.match(shortcode)  # These are actually morph/tone without a tone
        if m:
            name = m.group(1)
            return name, name + "_{morph}_{tone}"
        m = self.TONEONLY.match(shortcode)
        if m:
            name = m.group(1)
            return name, name + "_{tone}"
        return None, None

    def add_path(self, path):
        path, _ = os.path.splitext(path)
        shortcode = os.path.basename(path)
        alias, expansion = self.guess_alias(shortcode)
        self.codes[shortcode] = path
        if alias is None:
            return None
        self.code2alias[shortcode] = alias
        if alias not in self.aliases:
            self.aliases[alias] = expansion
        else:
            assert self.aliases[alias] == expansion

    def write_code_index(self, stream):
        for code, path in self.codes.items():
            alias = self.code2alias.get(code) or ''
            print(f"{code}\t{path}\t{alias}", file=stream)

    def write_alias_index(self, stream):
        for alias, expansion in self.aliases.items():
            print(f"{alias}\t{expansion}", file=stream)


def extract_zip(fo, root):
    zf = zipfile.ZipFile(fo, 'r')
    aliases = AliasCompiler()
    for zi in zf.infolist():
        if not zi.filename.startswith(root):
            continue
        if zi.filename == root:
            continue
        print('\t' + zi.filename[len(root):])
        target = os.path.join('mutant', os.path.basename(zi.filename))
        if not zi.is_dir():
            with open(target, 'wb') as tf:
                tf.write(zf.read(zi.filename))
            aliases.add_path(zi.filename[len(root):])
    with open("mutant/index.txt", 'at') as indexfile:
        aliases.write_code_index(indexfile)
    with open("mutant/aliases.txt", 'at') as indexfile:
        aliases.write_alias_index(indexfile)


def make_root():
    if os.path.exists('mutant'):
        ans = "?"
        while ans not in 'yn':
            ans = input("mutant already exists. Files may be overwritten. Would you like to continue? ")
            if not ans:
                ans = '?'
            ans = ans.lower()[0]
        if ans == 'n':
            sys.exit("Exiting")
    else:
        os.makedirs('mutant')


def main():
    args = parse_args()
    make_root()
    for url, root in DOWNLOADS:
        print(url)
        with open_zip(url) as fo:
            extract_zip(fo, root)


if __name__ == '__main__':
    main()
