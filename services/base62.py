import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]

    digits = []

    while num > 0:
        remainder = num % 62
        digits.append(BASE62_ALPHABET[remainder])
        num //= 62

    return "".join(reversed(digits))