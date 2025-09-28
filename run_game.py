import sys
import os

MIN_VER = (3, 12) # I haven't tested it on older versions, but I'm sure everything will be fine even with 3.10

if sys.version_info[:2] < MIN_VER:
    sys.exit(
        "This game requires Python {}.{}.".format(*MIN_VER)
    )
else:
    os.system('python game.py')  # hacky, I know...
