#!/usr/bin/env python3
# Copyright © 2021 Patrick Fu.

import os
import sys
import shutil
from typing import List, Dict

"""
Script for archive products.
"""

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(PROJ_ROOT)

from buildscripts.utils import get_out_dir, get_abi_from_cpu
from buildscripts.ziputil import zip_folders


class Archiver():
    def __init__(self, proj_name: str, build_type: str, target_os: str, lib_type: str) -> None:
        self.proj_name = proj_name
        self.build_type = build_type
        self.target_os = target_os
        self.lib_type = lib_type
        self.cpu_list: List[str] = []
        self.build_lang = 'c'
        self.version: str = '0.0.1.0-heads'

    def set_cpu_list(self, cpu_list: List[str]):
        self.cpu_list = cpu_list

    def set_build_lang(self, lang: str):
        self.build_lang = lang

    def set_version(self, version: str):
        # Only use semver and branch, like '1.2.3.888-main'
        self.version = '-'.join(version.split('-')[:2])

    def archive(self) -> Dict[str, str]:
        """Archive products and symbols into zip file

        Returns:
            Dict[str, str]:  {'products': '/full/path/to/products.zip', 'symbols': '/full/path/to/symbols.zip'}
        """
        print('\n[*] Start archiving {0} {1}...\n'.format(self.target_os, self.build_type))

        product_name = '{proj}-{ver}-{os}-{lib}-{lang}'.format(
            proj=self.proj_name,
            ver=self.version,
            os=self.target_os,
            lib=self.lib_type,
            lang=self.build_lang
        )

        products_dir = get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, '__products')

        if os.path.exists(products_dir):
            print('[*] remove {}'.format(products_dir))
            shutil.rmtree(products_dir)
        print('[*] mkdir {}'.format(products_dir))
        os.mkdir(products_dir)

        tmp_product_dir = os.path.join(products_dir, product_name)
        tmp_symbol_dir = os.path.join(products_dir, 'symbols-{}'.format(product_name))

        print('[*] mkdir {}'.format(tmp_product_dir))
        print('[*] mkdir {}'.format(tmp_symbol_dir))
        os.mkdir(tmp_product_dir)
        os.mkdir(tmp_symbol_dir)

        if self.target_os == 'ios' or self.target_os == 'mac':
            self._copy_darwin(tmp_product_dir, tmp_symbol_dir)

        products_zip_name = '{}.zip'.format(product_name)
        symbols_zip_name = 'symbols-{}.zip'.format(product_name)
        products_zip_path = os.path.join(products_dir, products_zip_name)
        symbols_zip_path = os.path.join(products_dir, symbols_zip_name)

        print('\n[*] Zip products: {0}, from: {1}'.format(products_zip_path, tmp_product_dir))
        zip_folders([tmp_product_dir], products_dir, products_zip_name, exclude_files=['.DS_Store'])

        print('\n[*] Zip symbols: {0}, from: {1}'.format(symbols_zip_path, tmp_symbol_dir))
        zip_folders([tmp_symbol_dir], products_dir, symbols_zip_name, exclude_files=['.DS_Store'])

        print('\n[*] Archive {0} {1} success!'.format(self.target_os, self.build_type))

        return {'products': products_zip_path, 'symbols': symbols_zip_path}

    def _copy_darwin(self, tmp_product_dir, tmp_symbol_dir):
        # Copy dSYM (only shared library)
        if self.lib_type == 'shared':
            print('\n[*] Copy Darwin dSYM...')
            for cpu in self.cpu_list:
                src_dir = get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, cpu)

                dsym_src = os.path.join(src_dir, '{}.dSYM'.format(self.proj_name))
                dsym_dst = os.path.join(tmp_symbol_dir, get_abi_from_cpu(self.target_os, cpu), '{}.dSYM'.format(self.proj_name))
                shutil.copytree(dsym_src, dsym_dst)

        # Copy XCFramework (Wrapper for shared or static library )
        print('\n[*] Copy Darwin XCFramework...')
        xcframework_src = os.path.join(get_out_dir(self.build_type, self.target_os, self.lib_type, self.build_lang, 'xcframework'), '{}.xcframework'.format(self.proj_name))
        xcframework_dst = os.path.join(tmp_product_dir, '{}.xcframework'.format(self.proj_name))
        shutil.copytree(xcframework_src, xcframework_dst)
