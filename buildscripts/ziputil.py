#!/usr/bin/env python3
# coding: utf-8
# Copyright © 2021 Patrick Fu.

import os
from typing import List
import zipfile


def unzip_file(src_zip_file, dst_folder):
    print("[*] [ZipUtil] Unzip `{}` to `{}`".format(src_zip_file, dst_folder))
    with zipfile.ZipFile(src_zip_file, 'r') as f:
        f.extractall(dst_folder)


def zip_single_file(src_file: str, dst_folder: str, zip_name: str) -> bool:
    if not os.path.exists(src_file):
        print("[*] [ZipUtil] src file: `{}` dose not exist!".format(src_file))
        return False

    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    zip_file = os.path.realpath(os.path.join(dst_folder, zip_name))
    basename = os.path.split(src_file)[-1]
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as f:
        _write_zip_content(src_file, f, basename)
    return True


def zip_folders(src_folder_list: List[str], dst_folder: str, zip_name: str, exclude_files: List[str]=[], append_dir_link: bool=True):
    def _is_exclude_file(fname):
        if exclude_files is None or len(exclude_files) == 0:
            return False
        for exclude_name in exclude_files:
            if fname.endswith(exclude_name):
                return True
        return False

    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    zip_file = os.path.realpath(os.path.join(dst_folder, zip_name))
    handle = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)

    for src_folder in src_folder_list:
        if not os.path.exists(src_folder):
            print("[*] [ZipUtil] SRC Folder: `{}` does not exist!".format(src_folder))
            continue

        filelist = []
        if os.path.isfile(src_folder) or os.path.islink(src_folder):
            filelist.append(src_folder)
        else:
            for root, dirs, files in os.walk(src_folder):
                for name in files:
                    if _is_exclude_file(name):
                        continue
                    filelist.append(os.path.join(root, name))
                if append_dir_link:
                    # Folder soft links are also added to the package list (compatible with macOS framework)
                    for name in dirs:
                        if os.path.islink(os.path.join(root, name)):
                            filelist.append(os.path.join(root, name))

        for tar in filelist:
            basename = os.path.split(src_folder)[-1]
            arcname = tar[len(src_folder):]
            filename = basename + arcname
            _write_zip_content(tar, handle, filename)

    handle.close()

    return True


def _write_zip_content(src_file, zip_handle, name_in_zip):
    if os.path.islink(src_file):
        print(">> zip link {}".format(name_in_zip))
        _zipLink = zipfile.ZipInfo(name_in_zip)
        _zipLink.create_system = 3
        # long type of hex val of '0xA1ED0000L',
        # say, symlink attr magic...
        _zipLink.external_attr = 2716663808
        zip_handle.writestr(_zipLink, os.readlink(src_file))
    else:
        print(">> zip file {0}".format(name_in_zip))
        zip_handle.write(src_file, name_in_zip)
