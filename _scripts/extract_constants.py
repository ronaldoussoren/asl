#!/usr/bin/env python3
"""
Helper script for updating the asl._constants module

Run this with new versions of the OSX SDK to update that
file (and forget to check for new APIs as well)
"""
import os
import re

literals = []

def is_int_literal(value):
    try:
        int(value, 0)
        return True
    except ValueError as msg:
        return False

def is_string_literal(value):
    return value[0] == '"' and value[-1] == '"' and len(value) > 1 and '"' not in value[1:-1]

COMMENT=re.compile('/\*(?:[^*]|(?:\*[^/]))*\*/')
def strip_comment(line):
    return ''.join(COMMENT.split(line))


with open("/usr/include/asl.h", "r") as fp:
    for line in fp:
        if line.startswith("#define"):
            line = strip_comment(line).strip()
            try:
                _, key, value = line.split(None, 2)
            except ValueError:
                continue

            if is_int_literal(value):
                literals.append((key, int(value, 0)))

            elif is_string_literal(value):
                literals.append((key, value[1:-1]))

            else:
                print("skip", repr(line), repr(key), repr(value))


with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "asl", "_constants.py"), "w") as fp:
    print("'''", file=fp)
    print("ASL constant definitions", file=fp)
    print("", file=fp)
    print("THIS FILE IS GENERATED, DON'T UPDATE MANUALLY", file=fp)
    print("'''", file=fp)
    print("", file=fp)
    for key, value in literals:
        print("%s = %r"%(key, value), file=fp)
