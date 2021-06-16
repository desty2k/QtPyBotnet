"""This file is only for creating GitHub releases.
To start QtPyBotnet server use 'python server.py'"""

import argparse

from __init__ import __version__


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__version__)
    parser.add_argument('-v', '--version', action='version', version='v{}'.format(__version__),
                        help='print version and exit')
    args = parser.parse_args()
