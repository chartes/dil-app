#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import random
import string
from hashlib import sha256
import datetime
from werkzeug.security import generate_password_hash

try:
    from api.config import settings
except ImportError:
    class settings:
        PWD_PREFIX = "fa-app@db"
        PWD_SUFFIX = "!,?"
        PWD_LENGTH = "150"


def pwd_generator():
    """
    Generate a random password.
    """
    chars = string.ascii_lowercase
    uppercase = random.choice([True, False])
    digits = random.choice([True, False])
    prefix = f"{settings.PWD_PREFIX}-{datetime.datetime.now().year}"
    suffix = random.choice(settings.PWD_SUFFIX.split(','))
    length = int(random.choice(settings.PWD_LENGTH.split(',')))
    rand = random.randint(5, 10)
    if uppercase:
        chars += string.ascii_uppercase
    if digits:
        chars += string.digits
    password = sha256("".join(random.choice(chars) for _ in range(length)).encode('utf-8')).hexdigest()[0:rand]
    return f'{prefix}-{password}{suffix}'



if __name__ == "__main__":
        res = pwd_generator()
        print(res)
        hash_pass = generate_password_hash(res)
        print(hash_pass)
        res = 'admin'
        hash_pass = generate_password_hash(res)
        print("-----------------")
        print(res)
        print(hash_pass)

