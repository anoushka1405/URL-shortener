from config import SHORT_CODE_OFFSET

import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def encode_base62(num: int) -> str:

    num += SHORT_CODE_OFFSET

    digits = []

    while num > 0:
        remainder = num % 62
        digits.append(BASE62_ALPHABET[remainder])
        num //= 62

    return "".join(reversed(digits))