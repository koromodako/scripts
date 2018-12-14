#!/usr/bin/env python3
# -!- encoding:utf8 -!-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: hid_decoder.py
#     date: 2018-05-05
#   author: paul.dautry
#  purpose:
#
#  license:
#    hid_decoder Decoder for USB HID data
#    Copyright (C) 2018 paul.dautry
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
#  IMPORTS
# =============================================================================
from keys import Key, Modifier
from keymap import KEYMAP
from pathlib import Path
from argparse import ArgumentParser
# =============================================================================
#  CLASSES
# =============================================================================
class HIDDecoder:
    def __init__(self, input_file, chars_only=False):
        self.num_locked = False
        self.input_file = input_file
        self.chars_only = chars_only

    def apply_keymap(self, mod, keys):
        index = 1 if mod == Modifier.LEFT_SHIFT else 0

        chars = []
        for k in keys:
            key_variants = KEYMAP[k]

            if k.name.startswith('KEY_PAD') and self.num_locked:
                index = 1

            chars.append(key_variants[index])

        return chars

    def decode_mouse(self, lbytes):
        raise NotImplementedError("not implemented.")

    def decode_keyboard(self, lbytes):
        mod = Modifier(lbytes[0])
        keys = [Key(k) for k in lbytes[2:]]
        mapped = self.apply_keymap(mod, keys)

        if mod == Modifier.NONE and keys.count(Key.NONE) == 6:
            return "Key released."

        if self.chars_only:
            return "{}".format(mapped)

        return "Key pressed: (mod={}) keys={} -> chars={}".format(mod.name, [k.name for k in keys], mapped)

    def decode_line(self, line):
        if len(line) == 0:
            return "[EMPTY]"

        lbytes = [int(e, 16) for e in line.split(':')]

        if len(lbytes) == 3:
            return self.decode_mouse(lbytes)

        elif len(lbytes) == 8:
            return self.decode_keyboard(lbytes)

        else:
            return "[NOT KEYBOARD DATA]"

    def decode(self):
        with self.input_file.open('r') as fp:
            for line in fp:
                line = line.strip()
                print(self.decode_line(line))
# =============================================================================
#  SCRIPT
# =============================================================================
if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('--chars-only', '-c', action='store_true')
    p.add_argument('input_file', type=Path, help="Input file to be decoded.")
    args = p.parse_args()

    decoder = HIDDecoder(args.input_file, args.chars_only)
    decoder.decode()