#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import os
import sys
import json
import time
import subprocess

"""
Generate library version string
"""

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_git_desc() -> str:
    git_cmd = ['git', '-C', PROJ_ROOT, 'describe', '--all', '--long', '--abbrev=10']
    git_desc = subprocess.check_output(git_cmd).decode('utf8').strip()
    git_desc = git_desc.replace('/', '_')
    git_desc = git_desc.replace('remotes_', '')
    git_desc = git_desc.replace('origin_', '')
    return git_desc


def get_git_revision() -> str:
    git_desc = _get_git_desc()
    index = git_desc.rfind('-')
    git_revision = git_desc[index+1:]
    return git_revision


def get_short_semver() -> str:
    version_file = os.path.join(PROJ_ROOT, 'version.json')
    with open(version_file, 'r') as fr:
        m = json.load(fr)
    return '{0}.{1}.{2}'.format(m['major'], m['minor'], m['patch'])


def get_long_semver():

    def __get_git_branch() -> str:
        git_desc = _get_git_desc()
        git_branch = git_desc[0:git_desc.find('-')]
        index = git_branch.find('_')
        if index >= 0:
            branch = git_branch[0:index]
            if 'tags' in branch:
                # If got the tags, means that it is on detached commit.
                branch = 'heads'
        else:
            branch = git_branch
        return branch

    ver = get_short_semver()
    branch = __get_git_branch()
    return '{0}-{1}'.format(ver, branch)


def get_full_version():
    semver = get_long_semver()
    date = time.strftime('%y%m%d-%H%M%S')
    revision = get_git_revision()
    return '{0}-{1}-{2}'.format(semver, date, revision)


def main(argv):
    ACTIONS = {
        'fullver': get_full_version,
        'semver': get_short_semver,
        'revision': get_git_revision
    }

    if len(argv) != 1 or argv[0] not in ACTIONS:
        __usage()
    else:
        print(ACTIONS[argv[0]]())


def __usage():
    print("""
    Usage:

    1. Get full version: ( e.g '1.2.3-main-210101-120000-g6ff87c4924')

        python3 version_generator.py fullver

    2. Get short semantic version: ( e.g. '1.2.3' )

        python3 version_generator.py semver

    3. Get git revision: ( e.g. 'g6ff87c4924' )

        python3 version_generator.py revision

    Note: Every time you get the `fullver`, build number will increase by 1.

    """)

if __name__ == '__main__':
    main(sys.argv[1:])
