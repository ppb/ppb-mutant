#!/usr/bin/env python3
import os
import sys
import urllib.request
import zipfile
import io
import argparse

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


def extract_zip(fo, root):
    zf = zipfile.ZipFile(fo, 'r')
    with open('mutant/index.txt', 'at') as index:
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
                print(zi.filename[len(root):], file=index)


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
