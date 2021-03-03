#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import os
import sys
import argparse
import subprocess

from buildscripts.builder import Builder
from buildscripts.archiver import Archiver

"""
Build entry
"""

PROJ_NAME = 'GNBuildExample'
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))

def __get_cpu_list_and_build_lang(args):
    cpu_list = []
    lang = 'c'
    if args.target_os is None:
        raise Exception('Target OS must be specified.')
    elif args.target_os == 'android':
        cpu_list = args.android_cpu
        lang = args.android_lang
    elif args.target_os == 'ios':
        cpu_list = args.ios_cpu
        lang = args.ios_lang
    elif args.target_os == 'mac':
        cpu_list = args.mac_cpu
        lang = args.mac_lang
    elif args.target_os == 'win':
        cpu_list = args.win_cpu
        lang = args.win_lang
    else:
        raise Exception('Unknown Target OS: {}.'.format(args.target_os))
    return (cpu_list, lang)

def __gen_gbe_version() -> str:
    cmd = [
        sys.executable,
        os.path.join(PROJ_ROOT, 'buildscripts', 'version_generator.py'),
        'fullver'
    ]
    return subprocess.check_output(cmd).decode('utf8').strip()

def __parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description='The root build script.')

    parser.add_argument('--build-type', type=str, choices=['debug', 'release'], default='release')
    parser.add_argument('--debug', dest='build_type', action='store_const', const='debug')

    parser.add_argument('--target-os', type=str, choices=['android', 'ios', 'mac', 'win'])
    parser.add_argument('--only-gen', default=False, action='store_true', help='Whether to generate only GN build files without actually compiling with ninja.')

    parser.add_argument('--lib-type', type=str, choices=['shared', 'static'], default='shared', help='Build shared or static lib')

    parser.add_argument('--upload', default=False, action='store_true', help='Whether to upload products to Coding Artifactory')

    # Args for Android
    parser.add_argument('--android', dest='target_os', action='store_const', const='android')
    parser.add_argument('--android-cpu', action='store', type=str, nargs='+', choices=['arm', 'arm64', 'x86', 'x64'], default=['arm', 'arm64', 'x86', 'x64'])
    parser.add_argument('--android-lang', type=str, choices=['java', 'c'], default='java')

    # Args for iOS
    parser.add_argument('--ios', dest='target_os', action='store_const', const='ios')
    parser.add_argument('--ios-cpu', action='store', type=str, nargs='+', choices=['arm', 'arm64', 'x64'], default=['arm', 'arm64', 'x64'])
    parser.add_argument('--ios-lang', type=str, choices=['objc', 'c'], default='objc')
    parser.add_argument('--ios-no-bitcode', default=False, action='store_true', help='Disable bitcode for iOS targets.')

    # Args for macOS
    parser.add_argument('--mac', dest='target_os', action='store_const', const='mac')
    parser.add_argument('--mac-cpu', action='store', type=str, nargs='+', choices=['arm64', 'x64'], default=['arm64', 'x64'])
    parser.add_argument('--mac-lang', type=str, choices=['objc', 'c'], default='objc')

    # Args for Windows
    parser.add_argument('--win', dest='target_os', action='store_const', const='win')
    parser.add_argument('--win-cpu', action='store', type=str, nargs='+', choices=['x86', 'x64'], default=['x64'])
    parser.add_argument('--win-lang', type=str, choices=['c'], default='c')

    return parser.parse_args(args)


def main(argv):
    os.chdir(PROJ_ROOT)
    args = __parse_args(argv)
    cpu_list, build_lang = __get_cpu_list_and_build_lang(args)
    gbe_version = __gen_gbe_version()

    print('\n[*] Version: {}'.format(gbe_version))

    # Build with `gn` and `ninja`
    print('\n' + '=' * 30)
    builder = Builder(PROJ_NAME, args.build_type, args.target_os, args.lib_type)
    builder.set_only_gen(args.only_gen)
    builder.set_cpu_list(cpu_list)
    builder.set_build_lang(build_lang)
    builder.set_version(gbe_version)
    builder.build()

    if args.only_gen:
        # Only gen complete, exit.
        return 0

    # Archive products and symbols into zip
    print('\n' + '=' * 30)
    archiver = Archiver(PROJ_NAME, args.build_type, args.target_os, args.lib_type)
    archiver.set_cpu_list(cpu_list)
    archiver.set_version(gbe_version)
    archiver.set_build_lang(build_lang)
    archive_result = archiver.archive()

    print('\n[*] All build success ^_^\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
