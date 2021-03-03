#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import os

"""
Util methods for gn build
"""

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_out_dir(build_type: str, target_os: str, lib_type: str, build_lang: str, cpu: str) -> str:
    """Get the gn build target's output dir path

    Args:
        build_type (str): release or debug
        target_os (str): android/ios/mac/win/...
        lib_type (str): shared or static
        lang (str): c/objc/java/...
        cpu (str): arm/arm64/x86/x64/...

    Returns:
        str: The output dir path
    """

    # e.g. "./_out/android_java/release/arm64/"
    path = os.path.join(
        PROJ_ROOT,
        '_out',
        '{0}-{1}-{2}'.format(target_os, lib_type, build_lang),
        build_type,
        cpu
    )
    return path


def get_abi_from_cpu(target_os: str, cpu: str) -> str:
    """Get the platform-specific abi naming of the cpu architecture

    Args:
        target_os (str): android/ios/mac/win/...
        cpu (str): arm/arm64/x86/x64/...

    Returns:
        str: The platform-specific abi naming of the cpu architecture
    """
    if cpu == 'arm':
        if target_os == 'ios' or target_os == 'mac':
            return 'armv7'
        elif target_os == 'android':
            return 'armeabi-v7a'
        elif target_os == 'win':
            return 'arm'

    elif cpu == 'arm64':
        if target_os == 'ios' or target_os == 'mac':
            return 'arm64'
        elif target_os == 'android':
            return 'arm64-v8a'
        elif target_os == 'win':
            return 'arm64'

    elif cpu == 'x86':
        if target_os == 'ios' or target_os == 'mac':
            return 'i386'
        elif target_os == 'android':
            return 'x86'
        elif target_os == 'win':
            return 'x86'

    elif cpu == 'x64':
        if target_os == 'ios' or target_os == 'mac':
            return 'x86_64'
        elif target_os == 'android':
            return 'x86_64'
        elif target_os == 'win':
            return 'x64'

    else: # Unknown cpu
        return cpu
