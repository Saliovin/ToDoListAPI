import math


# Fractional Implementation
def get_mid_fraction(prev_fraction, next_fraction):
    numerator = prev_fraction["numerator"] + next_fraction["numerator"]
    denominator = prev_fraction["denominator"] + next_fraction["denominator"]

    return numerator, denominator


# Lexorank Implementation
def get_mid_rank(prev_rank="0", next_rank="z"):
    rank = ""
    i = 0

    while True:
        prev_char = char_at(prev_rank, i, "0")
        next_char = char_at(next_rank, i, "z")

        if prev_char == next_char:
            rank += prev_char
            i += 1
            continue

        mid_char = mid(prev_char, next_char)

        if mid_char == prev_char or mid_char == next_char:
            rank += prev_char
            i += 1
            continue

        rank += mid_char
        break

    return rank


def char_at(s, i, default_char):
    if i >= len(s):
        return default_char

    return s[i]


def mid(prev_char, next_char):
    prev_char_code = ord(prev_char)
    next_char_code = ord(next_char)
    mid_char_code = prev_char_code + math.floor((next_char_code - prev_char_code) / 2)

    return chr(mid_char_code)
