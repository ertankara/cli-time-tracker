#! /usr/bin/env python3
import sys
from flags import get_corresponding_flag_action

given_flags = sys.argv
given_flags.pop(0)

for f in given_flags:
    get_corresponding_flag_action(f)
