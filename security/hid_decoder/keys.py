# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: keys.py
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
from enum import Flag, Enum
# =============================================================================
#  CLASSES
# =============================================================================
class Modifier(Flag):
    NONE = 0x00
    LEFT_CTRL = 0x01
    LEFT_SHIFT = 0x02
    LEFT_ALT = 0x04
    LEFT_GUI = 0x08
    RIGHT_CTRL = 0x10
    RIGHT_SHIFT = 0x20
    RIGHT_ALT = 0x40
    RIGHT_GUI = 0x80

class Key(Enum):
    NONE = 0x00
    ERROR_ROLL_OVER = 0x01
    POST_FAIL = 0x02
    ERROR_UNDEFINED = 0x03
    KEY_A = 0x04
    KEY_B = 0x05
    KEY_C = 0x06
    KEY_D = 0x07
    KEY_E = 0x08
    KEY_F = 0x09
    KEY_G = 0x0A
    KEY_H = 0x0B
    KEY_I = 0x0C
    KEY_J = 0x0D
    KEY_K = 0x0E
    KEY_L = 0x0F
    KEY_M = 0x10
    KEY_N = 0x11
    KEY_O = 0x12
    KEY_P = 0x13
    KEY_Q = 0x14
    KEY_R = 0x15
    KEY_S = 0x16
    KEY_T = 0x17
    KEY_U = 0x18
    KEY_V = 0x19
    KEY_W = 0x1A
    KEY_X = 0x1B
    KEY_Y = 0x1C
    KEY_Z = 0x1D
    KEY_1 = 0x1E
    KEY_2 = 0x1F
    KEY_3 = 0x20
    KEY_4 = 0x21
    KEY_5 = 0x22
    KEY_6 = 0x23
    KEY_7 = 0x24
    KEY_8 = 0x25
    KEY_9 = 0x26
    KEY_0 = 0x27
    KEY_ENTER = 0x28
    KEY_ESCAPE = 0x29
    KEY_DELETE = 0x2A
    KEY_TAB = 0x2B
    KEY_SPACE = 0x2C
    KEY_MINUS = 0x2D
    KEY_EQUAL = 0x2E
    KEY_LEFT_BRACKET = 0x2F
    KEY_RIGHT_BRACKET = 0x30
    KEY_BACKSLASH = 0x31
    KEY_HASH = 0x32
    KEY_SEMICOLON = 0x33
    KEY_QUOTE = 0x34
    KEY_GRAVE_ACCENT = 0x35
    KEY_COMMA = 0x36
    KEY_DOT = 0x37
    KEY_SLASH = 0x38
    KEY_CAPS_LOCK = 0x39
    KEY_F1 = 0x3A
    KEY_F2 = 0x3B
    KEY_F3 = 0x3C
    KEY_F4 = 0x3D
    KEY_F5 = 0x3E
    KEY_F6 = 0x3F
    KEY_F7 = 0x40
    KEY_F8 = 0x41
    KEY_F9 = 0x42
    KEY_F10 = 0x43
    KEY_F11 = 0x44
    KEY_F12 = 0x45
    KEY_PRINT_SCREEN = 0x46
    KEY_SCROLL_LOCK = 0x47
    KEY_PAUSE = 0x48
    KEY_INSERT = 0x49
    KEY_HOME = 0x4A
    KEY_PAGE_UP = 0x4B
    KEY_DELETE_FWD = 0x4C
    KEY_END = 0x4D
    KEY_PAGE_DOWN = 0x4E
    KEY_RIGHT_ARROW = 0x4F
    KEY_LEFT_ARROW = 0x50
    KEY_DOWN_ARROW = 0x51
    KEY_UP_ARROW = 0x52
    KEY_NUM_LOCK = 0x53
    KEY_PAD_SLASH = 0x54
    KEY_PAD_STAR = 0x55
    KEY_PAD_MINUS = 0x56
    KEY_PAD_PLUS = 0x57
    KEY_PAD_RETURN = 0x58
    KEY_PAD_1 = 0x59
    KEY_PAD_2 = 0x5A
    KEY_PAD_3 = 0x5B
    KEY_PAD_4 = 0x5C
    KEY_PAD_5 = 0x5D
    KEY_PAD_6 = 0x5E
    KEY_PAD_7 = 0x5F
    KEY_PAD_8 = 0x60
    KEY_PAD_9 = 0x61
    KEY_PAD_0 = 0x62
    KEY_PAD_DOT = 0x63
    KEY_NON_US_BACKSLASH = 0x64
    KEY_APPLICATION = 0x65
    KEY_POWER = 0x66
    KEY_PAD_EQUAL = 0x67
    KEY_F13 = 0x68
    KEY_F14 = 0x69
    KEY_F15 = 0x6A
    KEY_F16 = 0x6B
    KEY_F17 = 0x6C
    KEY_F18 = 0x6D
    KEY_F19 = 0x6E
    KEY_F20 = 0x6F
    KEY_F21 = 0x70
    KEY_F22 = 0x71
    KEY_F23 = 0x72
    KEY_F24 = 0x73
    KEY_EXECUTE = 0x74
    KEY_HELP = 0x75
    KEY_MENU = 0x76
    KEY_SELECT = 0x77
    KEY_STOP = 0x78
    KEY_AGAIN = 0x79
    KEY_UNDO = 0x7A
    KEY_CUT = 0x7B
    KEY_COPY = 0x7C
    KEY_PASTE = 0x7D
    KEY_FIND = 0x7E
    KEY_MUTE = 0x7F
    KEY_VOLUME_UP = 0x80
    KEY_VOLUME_DOWN = 0x81
    KEY_LOCKING_CAPS_LOCK = 0x82
    KEY_LOCKING_NUM_LOCK = 0x83
    KEY_LOCKING_SCROLL_LOCK = 0x84
    KEY_PAD_COMMA = 0x85
    KEY_PAD_EQUAL_SIGN = 0x86
    KEY_INTERNATIONAL1 = 0x87
    KEY_INTERNATIONAL2 = 0x88
    KEY_INTERNATIONAL3 = 0x89
    KEY_INTERNATIONAL4 = 0x8A
    KEY_INTERNATIONAL5 = 0x8B
    KEY_INTERNATIONAL6 = 0x8C
    KEY_INTERNATIONAL7 = 0x8D
    KEY_INTERNATIONAL8 = 0x8E
    KEY_INTERNATIONAL9 = 0x8F
    KEY_LANG1 = 0x90
    KEY_LANG2 = 0x91
    KEY_LANG3 = 0x92
    KEY_LANG4 = 0x93
    KEY_LANG5 = 0x94
    KEY_LANG6 = 0x95
    KEY_LANG7 = 0x96
    KEY_LANG8 = 0x97
    KEY_LANG9 = 0x98
    KEY_ALT_ERASE = 0x99
    KEY_SYSREQ_ATTENTION = 0x9A
    KEY_CANCEL = 0x9B
    KEY_CLEAR = 0x9C
    KEY_PRIOR = 0x9D
    KEY_RETURN = 0x9E
    KEY_SEPARATOR = 0x9F
    KEY_OUT = 0xA0
    KEY_OPER = 0xA1
    KEY_CLEAR_AGAIN = 0xA2
    KEY_CRSEL_PROPS = 0xA3
    KEY_EXSEL = 0xA4
    #RESERVED = 0xA5-0xAF
    KEY_PAD_00 = 0xB0
    KEY_PAD_000 = 0xB1
    THOUSANDS_SEP = 0xB2
    DECIMAL_SEP = 0xB3
    CURRENCY_UNIT = 0xB4
    CURRENCY_SUB_UNIT = 0xB5
    KEY_PAD_LEFT_PARENTHESIS = 0xB6
    KEY_PAD_RIGHT_PARENTHESIS = 0xB7
    KEY_PAD_LEFT_BRACE = 0xB8
    KEY_PAD_RIGHT_BRACE = 0xB9
    KEY_PAD_TAB = 0xBA
    KEY_PAD_BACKSPACE = 0xBB
    KEY_PAD_A = 0xBC
    KEY_PAD_B = 0xBD
    KEY_PAD_C = 0xBE
    KEY_PAD_D = 0xBF
    KEY_PAD_E = 0xC0
    KEY_PAD_F = 0xC1
    KEY_PAD_XOR = 0xC2
    KEY_PAD_CIRCUMFLEX_ACCENT = 0xC3
    KEY_PAD_PERCENT = 0xC4
    KEY_PAD_LT = 0xC5
    KEY_PAD_GT = 0xC6
    KEY_PAD_AND = 0xC7
    KEY_PAD_LOGICAL_AND = 0xC8
    KEY_PAD_PIPE = 0xC9
    KEY_PAD_LOGICAL_OR = 0xCA
    KEY_PAD_COLON = 0xCB
    KEY_PAD_HASH = 0xCC
    KEY_PAD_SPACE = 0xCD
    KEY_PAD_AT = 0xCE
    KEY_PAD_EXCLAMATION = 0xCF
    KEY_PAD_MEMORY_STORE = 0xD0
    KEY_PAD_MEMORY_RECALL = 0xD1
    KEY_PAD_MEMORY_CLEAR = 0xD2
    KEY_PAD_MEMORY_ADD = 0xD3
    KEY_PAD_MEMORY_SUBTRACT = 0xD4
    KEY_PAD_MEMORY_MULTIPLY = 0xD5
    KEY_PAD_MEMORY_DIVIDE = 0xD6
    KEY_PAD_PLUS_MINUS = 0xD7
    KEY_PAD_CLEAR = 0xD8
    KEY_PAD_CLEAR_ENTRY = 0xD9
    KEY_PAD_BINARY = 0xDA
    KEY_PAD_OCTAL = 0xDB
    KEY_PAD_DECIMAL = 0xDC
    KEY_PAD_HEXADECIMAL = 0xDD
    #RESERVED = 0xDE-0xDF
    KEY_LEFT_CTRL = 0xE0
    KEY_LEFT_SHIFT = 0xE1
    KEY_LEFT_ALT = 0xE2
    KEY_LEFT_GUI = 0xE3
    KEY_RIGHT_CTRL = 0xE4
    KEY_RIGHT_SHIFT = 0xE5
    KEY_RIGHT_ALT = 0xE6
    KEY_RIGHT_GUI = 0xE7
    #RESERVED = 0xE8-0xFFFF