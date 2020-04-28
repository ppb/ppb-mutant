#!/usr/bin/env python3
import os
import urllib.request
import zipfile
import io
import argparse
import re
import pathlib
import contextlib

DOWNLOADS = [
    ('https://mutant.tech/dl/2020.04/mtnt_2020.04_short_png128.zip', 'mtnt_2020.02_short_png128/emoji/'),
    ('https://mutant.tech/dl/vip/mutstd_vip_2018.04_all.zip', 'mutstd_vip_2018.04_all/emoji/png-128px/'),
    ('https://mutant.tech/dl/special/mtnt_special_s3.zip', 'mtnt_special_s3/emoji/png-128/'),
]

# Copied from __init__.py
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



@contextlib.contextmanager
def enter_dir(dest):
    old_dir = pathlib.Path.cwd()
    os.chdir(dest)
    try:
        yield
    finally:
        os.chdir(old_dir)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Download the Mutant Standard emoji to the source directory.',
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

    def add_path(self, path, *, alias=None, expansion=None):
        path, _ = os.path.splitext(path)
        shortcode = os.path.basename(path)
        if alias is None:
            alias, expansion = self.guess_alias(shortcode)
        else:
            # Alias is given to us
            if expansion == 1:
                expansion = alias + "_{tone}"
            elif expansion == 2:
                expansion = alias + "_{morph}_{tone}"
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
        target = os.path.join('_assets', os.path.basename(zi.filename))
        if not zi.is_dir():
            with open(target, 'wb') as tf:
                tf.write(zf.read(zi.filename))
            aliases.add_path(zi.filename[len(root):])
    with open("_assets/index.txt", 'at') as indexfile:
        aliases.write_code_index(indexfile)
    with open("_assets/aliases.txt", 'at') as indexfile:
        aliases.write_alias_index(indexfile)


def make_root():
    if not os.path.exists('_assets'):
        os.makedirs('_assets')


def main():
    args = parse_args()
    rootdir = pathlib.Path(__file__).absolute().parent / 'ppb_mutant'

    with enter_dir(rootdir):
        make_root()
        for url, root in DOWNLOADS:
            print(url)
            with open_zip(url) as fo:
                extract_zip(fo, root)


if __name__ == '__main__':
    main()
