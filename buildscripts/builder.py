#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import os
import sys
import shutil
import subprocess
from typing import List

"""
Script for build all platforms.
"""

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(PROJ_ROOT)

from buildscripts.utils import get_out_dir, get_abi_from_cpu


class Builder():
    def __init__(self, proj_name: str, build_type: str, target_os: str, lib_type: str) -> None:
        self.proj_name = proj_name
        self.build_type = build_type
        self.target_os = target_os
        self.lib_type = lib_type
        self.cpu_list: List[str] = []
        self.build_lang = 'c'
        self.only_gen = False
        self.version: str = 'unknown'
        self.common_args = [
            '--build-type', build_type,
            '--target-os', target_os,
            '--lib-type', lib_type
        ]

    def set_version(self, version: str):
        self.version = version
        self.common_args.extend(['--version', self.version])

    def set_only_gen(self, only_gen: bool):
        self.only_gen = only_gen
        if self.only_gen:
            print('\n[*] Set only gen, do not build.')
            self.common_args.append('--only-gen')

    def set_cpu_list(self, cpu_list: List[str]):
        self.cpu_list = cpu_list

    def set_build_lang(self, lang: str):
        if lang == 'java' and self.target_os != 'android':
            raise Exception('Java build lang only available for Android.')
        if lang == 'objc' and self.target_os != 'ios' and self.target_os != 'mac':
            raise Exception('Objective-C build lang only available for iOS/macOS.')
        self.build_lang = lang

    def build(self):
        """
        Invoke the ./gn.py to run `gn gen` and `ninja` build
        """
        print('\n[*] Start building {0} {1}...'.format(self.target_os, self.build_type))
        for cpu in self.cpu_list:
            print('\n[*] Build arch {0} for {1} {2}...'.format(cpu, self.target_os, self.build_type))
            build_cmd = [sys.executable, '-u', os.path.join(PROJ_ROOT, 'buildscripts', 'gn.py')]
            build_cmd.extend(self.common_args)
            build_cmd += ['--{0}-cpu'.format(self.target_os), cpu]
            build_cmd += ['--{0}-lang'.format(self.target_os), self.build_lang]
            print('\n[*] Execute command: {}'.format(' '.join(build_cmd)))
            subprocess.check_call(build_cmd)

        if not self.only_gen:
            if self.target_os == 'ios' or self.target_os == 'mac':
                print('\n[*] Creating Darwin XCFramework...')
                self._create_darwin_xcframework()

        print('\n[*] {0} {1} {2} success!'.format(
            'Build' if not self.only_gen else 'Only gen',
             self.target_os,
             self.build_type
        ))

    def _create_darwin_xcframework(self):
        """
        Use xcrun to create XCFramework for iOS/macOS
        """
        if self.target_os != 'ios' and self.target_os != 'mac':
            raise Exception('[_create_darwin_xcframework] only work for iOS/macOS.')

        def __lipo_combine_binary(self, src_arch: str, dst_arch: str):
            """
            Use lipo to combine 'src_arch' binary into 'dst_arch' binary.
            > Because XCFramework requires that multi arch in the same platform have to be in one combined binary.
            """
            binary_file = 'lib{}.a'.format(self.proj_name) if self.lib_type == 'static' else '{0}.framework/{0}'.format(self.proj_name)

            src_binary = os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, src_arch), binary_file)
            dst_binary = os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, dst_arch), binary_file)

            lipo_info_cmd = ['xcrun', 'lipo', '-info', dst_binary]
            print('\n[*] Check binary\'s arch.')
            print('[*] Execute command: {}'.format(' '.join(lipo_info_cmd)))
            res = subprocess.check_output(lipo_info_cmd).decode('utf8').strip()
            print(res)

            # If dst binary does not contains 'src_arch', combine src binary into dst.
            if get_abi_from_cpu(self.target_os, src_arch) not in res:
                lipo_create_cmd = ['xcrun', 'lipo', '-create',
                    src_binary, dst_binary,
                    '-output', dst_binary
                ]
                print('\n[*] Combine {0} into {1} binary with lipo.'.format(src_arch, dst_arch))
                print('[*] Execute command: {}'.format(' '.join(lipo_create_cmd)))
                subprocess.check_call(lipo_create_cmd)

        # Combine iOS armv7 into arm64 binary
        if self.target_os == 'ios' and 'arm' in self.cpu_list and 'arm64' in self.cpu_list:
            __lipo_combine_binary(self, 'arm', 'arm64')

        # Combine macOS arm64 into x86_64 binary
        if self.target_os == 'mac' and 'arm64' in self.cpu_list and 'x64' in self.cpu_list:
            __lipo_combine_binary(self, 'arm64', 'x64')

        # Create the XCFramework
        xcframework_output = os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, 'xcframework'), '%s.xcframework' % self.proj_name)
        if os.path.exists(xcframework_output):
            shutil.rmtree(xcframework_output)

        xcframework_cmd = ['xcrun', 'xcodebuild', '-create-xcframework']
        for cpu in self.cpu_list:
            if self.target_os == 'ios' and cpu == 'arm':
                continue # iOS arm have been combined into arm64 binary
            if self.target_os == 'mac' and cpu == 'arm64':
                continue # macOS arm64 have been combined into x64 binary

            if self.lib_type == 'shared':
                xcframework_cmd.extend([
                    '-framework',
                    os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, cpu), '{}.framework'.format(self.proj_name))
                ])
            elif self.lib_type == 'static':
                xcframework_cmd.extend([
                    '-library',
                    os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, cpu), 'lib{}.a'.format(self.proj_name)),
                    '-headers',
                    os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, cpu), 'include'),
                ])

        xcframework_cmd.extend([
            '-output',
            xcframework_output
        ])

        print('\n[*] Execute command: {}'.format(' '.join(xcframework_cmd)))
        subprocess.check_call(xcframework_cmd)
