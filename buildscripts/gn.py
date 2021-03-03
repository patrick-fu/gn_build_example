#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import argparse
import subprocess
import sys
import os

"""
Script used to call specific single `gn gen` and `ninja` commands
"""

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(PROJ_ROOT)

from buildscripts.utils import get_out_dir


def __to_command_line(gn_args):
    def merge(key, value):
        if type(value) is bool:
            return '%s=%s' % (key, 'true' if value else 'false')
        if type(value) is list:
            return '%s=[%s]' % (key, ','.join('"%s"' % v for v in value))
        return '%s="%s"' % (key, value)
    return [merge(x, y) for x, y in gn_args.items()]


def __to_gn_args(args):
    gn_args = {}
    gn_args['is_official_build'] = args.build_type == 'release'
    gn_args['gbe_version'] = '\\"{}\\"'.format(args.version)

    if args.target_os == 'ios':
        gn_args['target_os'] = 'ios'
        gn_args['enable_ios_bitcode'] = not args.ios_no_bitcode
        gn_args['ios_app_bundle_id_prefix'] = 'com.paaatrick'
        gn_args['enable_dsyms'] = True # Always enable dsyms even debug

        # If there are multiple 'Apple Development' certificates in your keychain
        # please fill in the Team Name pattern of the specified certificate
        gn_args['ios_code_signing_identity_team_name'] = '' # e.g. 'Zego'

        if args.lib_type == 'shared':
            if args.ios_lang == 'objc':
                gn_args['build_ios_objc_shared'] = True
            elif args.ios_lang == 'c':
                gn_args['build_ios_common_shared'] = True
        elif args.lib_type == 'static':
            if args.ios_lang == 'objc':
                gn_args['build_ios_objc_static'] = True
            elif args.ios_lang == 'c':
                gn_args['build_ios_common_static'] = True

    elif args.target_os == 'mac':
        gn_args['target_os'] = 'mac'
        gn_args['mac_app_bundle_id_prefix'] = 'com.paaatrick'
        gn_args['enable_dsyms'] = True # Always enable dsyms even debug

        if args.lib_type == 'shared':
            if args.mac_lang == 'objc':
                gn_args['build_mac_objc_shared'] = True
            elif args.mac_lang == 'c':
                gn_args['build_mac_common_shared'] = True
        elif args.lib_type == 'static':
            if args.mac_lang == 'objc':
                gn_args['build_mac_objc_static'] = True
            elif args.mac_lang == 'c':
                gn_args['build_mac_common_static'] = True

    else:
        raise Exception('Unknown target os: %s' % args.target_os)

    if args.target_os == 'android':
        gn_args['target_cpu'] = args.android_cpu
    elif args.target_os == 'ios':
        gn_args['target_cpu'] = args.ios_cpu
    elif args.target_os == 'mac':
        gn_args['target_cpu'] = args.mac_cpu

    # Make sure host_cpu matches the bit width of target_cpu on x86.
    # if gn_args['target_cpu'] == 'x86':
    #     gn_args['host_cpu'] = 'x86'

    # Sanitizers.
    if args.msan:
        gn_args['is_msan'] = True
    if args.asan:
        gn_args['is_asan'] = True
    if args.tsan:
        gn_args['is_tsan'] = True
    if args.lsan:
        gn_args['is_lsan'] = True
    if args.ubsan:
        gn_args['is_ubsan'] = True
    return gn_args

def __parse_args(args):
    args = args[1:]
    parser = argparse.ArgumentParser(description='A script run `gn gen`.')

    parser.add_argument('--build-type', type=str, choices=['debug', 'release'], default='release')
    parser.add_argument('--target-os', type=str, choices=['android', 'ios', 'mac', 'win'])
    parser.add_argument('--only-gen', default=False, action='store_true', help='Whether to generate only GN build files without actually compiling with ninja.')

    parser.add_argument('--version', type=str, default='Unknown', help='Internal version string (hard code in the lib, the `getVersion() function`)')

    parser.add_argument('--lib-type', type=str, choices=['shared', 'static'], default='shared')

    # Args for Android
    parser.add_argument('--android', dest='target_os', action='store_const', const='android')
    parser.add_argument('--android-cpu', type=str, choices=['arm', 'arm64', 'x86', 'x64'], default='arm')
    parser.add_argument('--android-lang', type=str, choices=['java', 'c'], default='java')

    # Args for iOS
    parser.add_argument('--ios', dest='target_os', action='store_const', const='ios')
    parser.add_argument('--ios-cpu', type=str, choices=['arm', 'arm64', 'x64'], default='arm64')
    parser.add_argument('--ios-lang', type=str, choices=['objc', 'c'], default='objc')
    parser.add_argument('--ios-no-bitcode', default=False, action='store_true', help='Disable bitcode for iOS targets.')

    # Args for macOS
    parser.add_argument('--mac', dest='target_os', action='store_const', const='mac')
    parser.add_argument('--mac-cpu', type=str, choices=['arm64', 'x64'], default='x64')
    parser.add_argument('--mac-lang', type=str, choices=['objc', 'c'], default='objc')

    # Args for Windows
    parser.add_argument('--win', dest='target_os', action='store_const', const='win')
    parser.add_argument('--win-cpu', type=str, choices=['x86', 'x64'], default='x64')
    parser.add_argument('--win-lang', type=str, choices=['c'], default='c')

    # Sanitizers.
    parser.add_argument('--asan', default=False, action='store_true')
    parser.add_argument('--lsan', default=False, action='store_true')
    parser.add_argument('--msan', default=False, action='store_true')
    parser.add_argument('--tsan', default=False, action='store_true')
    parser.add_argument('--ubsan', default=False, action='store_true')

    return parser.parse_args(args)

def main(argv):
    args = __parse_args(argv)

    exe = '.exe' if sys.platform.startswith(('cygwin', 'win')) else ''
    platform = ''
    if sys.platform == 'darwin':
        platform = 'darwin'
    elif sys.platform.startswith(('cygwin', 'win')):
        platform = 'windows'
    elif sys.platform.startswith('linux'):
        platform = 'linux'

    gn_cmd = [
        os.path.join(PROJ_ROOT, 'buildtools', platform, 'gn{}'.format(exe)),
        'gen',
        '--check',
        '-v'
    ]

    if args.target_os is None:
        raise Exception('Target OS must be specified.')

    if platform == 'darwin':
        # On the Mac, generate an Xcode project by default.
        gn_cmd.append('--ide=xcode')
        gn_cmd.append('--xcode-project=GNBuildExample')
        gn_cmd.append('--xcode-build-system=new')
    elif platform == 'windows':
        # On Windows, generate a Visual Studio project.
        gn_cmd.append('--ide=vs')

    gn_args = __to_command_line(__to_gn_args(args))
    out_dir = get_out_dir(
        args.build_type,
        args.target_os,
        args.lib_type,
        args.__getattribute__('{}_lang'.format(args.target_os)),
        args.__getattribute__('{}_cpu'.format(args.target_os))
    )

    gn_cmd.append(out_dir)
    gn_cmd.append('--args=%s' % ' '.join(gn_args))

    print('\n[*] GN command: {}'.format(' '.join(gn_cmd)))
    print('\n[*] Generating GN files in: {}'.format(out_dir))
    try:
        gn_call_result = subprocess.call(gn_cmd, cwd=PROJ_ROOT)
    except subprocess.CalledProcessError as exc:
        print('[*] Failed to generate gn files: ', exc.returncode, exc.output)
        sys.exit(1)

    if gn_call_result != 0:
        # GN gen failed, exit early
        print('[*] Failed to generate gn files.')
        return gn_call_result

    # Generate/Replace the compile commands database in out.
    # It does not run a actual ninja build command,
    # but just generate a full ninja compile commands.
    compile_cmd_gen_cmd = [
        os.path.join(PROJ_ROOT, 'buildtools', platform, 'ninja{}'.format(exe)),
        '-C',
        out_dir,
        '-t',
        'compdb',
        'cc',
        'cxx',
        'objc',
        'objcxx',
        'asm',
    ]

    print('\n[*] Run ninja -t compdb command: {}'.format(' '.join(compile_cmd_gen_cmd)))
    try:
        contents = subprocess.check_output(compile_cmd_gen_cmd, cwd=PROJ_ROOT)
        with open(os.path.join(out_dir, 'compile_commands.json'), 'wb') as fw:
            fw.write(contents)
    except subprocess.CalledProcessError as exc:
        print('[*] Failed to run ninja -t compdb: ', exc.returncode, exc.output)
        sys.exit(1)

    # Run ninja build command to compile.
    if not args.only_gen:
        compile_cmd = [
            os.path.join(PROJ_ROOT, 'buildtools', platform, 'ninja{}'.format(exe)),
            '-v',
            '-C',
            out_dir
        ]

        print('\n[*] Run ninja build command: {}'.format(' '.join(compile_cmd)))
        try:
            ninja_build_result = subprocess.check_call(compile_cmd, cwd=PROJ_ROOT)
        except subprocess.CalledProcessError as exc:
            print('[*] Failed to run ninja build: ', exc.returncode, exc.output)
            sys.exit(1)

    return ninja_build_result


if __name__ == '__main__':
    sys.exit(main(sys.argv))