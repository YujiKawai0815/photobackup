#! env python
# -*- coding: utf-8 -*-
import json
import logging
import shutil
from argparse import ArgumentParser
from pathlib import Path

# PhotoBackup.photo_backup
# Date: 2020/01/25
# Filename: photo_backup 

__author__ = 'Yuji'
__date__ = "2020/01/25"
__file_dir__ = (Path.cwd() / __file__).parent
__log_path__ = __file_dir__ / 'PhotoBackup.log'
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(sh)
fh = logging.FileHandler(__log_path__)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(fh)


def load_json(path):
    with Path(path).open('r') as f:
        return json.load(f)


def dump_json(data, path):
    with Path(path).open('w') as f:
        json.dump(data, f, indent=2)


def load_file_dict(dst_dir):
    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    file_dict_path = Path(dst_dir) / 'backup_info.json'
    if not file_dict_path.exists():
        file_dict = list()
        dump_json(file_dict, file_dict_path)
    file_dict = set(load_json(file_dict_path))
    return file_dict


def dump_file_dict(file_dict, dst_dir):
    file_dict_path = Path(dst_dir) / 'backup_info.json'
    dump_json(list(file_dict), file_dict_path)


def is_backedup(path, file_dict):
    return path.as_posix() in file_dict or any([exclude_word in path.as_posix() for exclude_word in ['output', 'temp']])


def backup_photo(src_dir, dst_dir):
    file_dict = load_file_dict(dst_dir)
    i = 0
    for src_path in Path(src_dir).rglob('*'):
        if src_path.is_file():
            rel_path = src_path.relative_to(src_dir)
            if not is_backedup(rel_path, file_dict):
                dst_path = dst_dir / rel_path
                if dst_path.exists():
                    file_dict.add(rel_path.as_posix())
                    continue
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                log.info('copy {}'.format(rel_path))
                shutil.copy2(src_path, dst_path)
                file_dict.add(rel_path.as_posix())
                i += 1
                if i % 10 == 0:
                    dump_file_dict(file_dict, dst_dir)


def get_args():
    parser = ArgumentParser(description='Program to backup files without updating already backedup files')
    parser.add_argument('--src_dir', default=None)
    parser.add_argument('--dst_dir', default=None)
    args = parser.parse_args()
    return Path(args.src_dir), Path(args.dst_dir)


def run_backup():
    try:
        log.info('start backup')
        src_dir, dst_dir = get_args()
        backup_photo(src_dir, dst_dir)
        log.info('complete backup')
    except Exception as e:
        import traceback
        log.error(e)
        log.error("tb: %s", "".join(traceback.format_stack()))
        raise e


if __name__ == '__main__':
    run_backup()
