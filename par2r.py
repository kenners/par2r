#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""par2r

A Python 3 wrapper to recursively call par2 in subdirectories for specified filetypes.
"""

import os, sys, subprocess, argparse

def main():
    parser = argparse.ArgumentParser(description="A Python3 wrapper to recursively use par2 in nested directories.")
    parser.add_argument("action", type=str, choices=["create", "c", "verify", "v", "repair", "r"], default="create", help="The desired action to perform")
    parser.add_argument("dir", type=is_directory, default=os.getcwd(), help="The parent directory to recursively create par2 files in")
    args = parser.parse_args()
    if args.action in ("create", "c"):
        output = create(args.dir)
    elif args.action in ("verify", "v"):
        output = verify(args.dir)
    elif args.action in ("repair", "r"):
        output = repair(args.dir)
    else:
        msg = "No arguments supplied"
        raise parser.ArgumentTypeError(msg)
    return parser.exit()

# Filetypes we care about
filetypes = ('.dng','.jpg', '.tif', '.tiff', '.jpeg', '.mp4', '.mov', '.m4v', '.avi', '.lrcat')

def get_target_dirs(parent_dir):
    """Returns a list of children directories containing at least one file of our target filetypes"""
    # Get a list of the directories that contain one of our desired filetypes
    # Thanks to http://stackoverflow.com/a/9997442 for inspiration
    target_dirs = [folder for folder, subfolders, files in os.walk(parent_dir) for file_ in files if os.path.splitext(file_)[1] in filetypes]
    # Remove any dupes
    target_dirs = list(set(target_dirs))
    return target_dirs

def create_par(target_dir):
    """Creates a par2 archive with the provided name"""
    os.chdir(target_dir)
    filename = '{0}.par2'.format(os.path.basename(target_dir))
    par2 = subprocess.call(['par2', 'create', '-r10', '-t+', '-n1', '-q', '-q', filename, '*'])
    return par2

def verify_par(target_dir):
    """Verifies a par2 archive with the provided name"""
    os.chdir(target_dir)
    filename = '{0}.par2'.format(os.path.basename(target_dir))
    if os.path.isfile(filename):
        par2 = subprocess.call(['par2', 'verify', '-q', '-q', filename, '*'])
    else:
        par2 = 'missing'
    return par2

def repair_par(target_dir):
    """Repairs a par2 archive with the provided name"""
    os.chdir(target_dir)
    filename = '{0}.par2'.format(os.path.basename(target_dir))
    if os.path.isfile(filename):
        par2 = subprocess.call(['par2', 'repair', '-q', '-q', filename, '*'])
    else:
        par2 = 10
    return par2

def verify(parent_dir):
    """Recursively verifies par2 archives for each subdirectory containing the desired filetype"""
    targets = get_target_dirs(parent_dir)
    output = {target:verify_par(target) for target in targets}
    for result in output:
        if output[result] == 0:
            print("OK: data verified intact for par2 archive in {0}".format(result))
        elif output[result] == 1:
            print("***REPAIRS NEEDED***: par2 exited with return code {0} in {1}".format(output[result], result))
        elif output[result] == 10:
            print("ERROR: no par2 archive found in {0}".format(result))
        elif output[result] == 2:
            print("ERROR: repairs needed but ***insufficient recovery data***. par2 exited with return code {0} in {1}".format(output[result], result))
        else:
            print("ERROR: something has gone wrong! par2 exited with return code {0} in {1}".format(output[result], result))
    return

def repair(parent_dir):
    """Recursively repairs par2 archives for each subdirectory containing the desired filetype"""
    targets = get_target_dirs(parent_dir)
    output = {target:repair_par(target) for target in targets}
    for result in output:
        if output[result] == 0:
            print("OK: no repairs required or successfully repaired par2 archive in {0}".format(result))
        elif output[result] == 1:
            print("ERROR: repairing failed (?cause). par2 exited with return code {0} in {1}".format(output[result], result))
        elif output[result] == 10:
            print("ERROR: no par2 archive found in {0}".format(result))
        elif output[result] == 2:
            print("ERROR: repairing failed - insufficient recovery data. par2 exited with return code {0} in {1}".format(output[result], result))
        else:
            print("ERROR: repairing failed (?cause). par2 exited with return code {0} in {1}".format(output[result], result))
    return


def create(parent_dir):
    """Recursively creates a par2 archives for each subdirectory containing the desired filetype"""
    targets = get_target_dirs(parent_dir)
    output = {target:create_par(target) for target in targets}
    for result in output:
        if output[result] == 0:
            print("OK: created par2 archive in {0}".format(result))
        elif output[result] > 0:
            print("ERROR: par2tbb exited with return code {0} in {1}".format(output[result], result))
    return

def is_directory(directory):
    if not os.path.isdir(directory):
        msg = "{0} is not a valid directory".format(directory)
        raise argparse.ArgumentTypeError(msg)
    return directory

if __name__ == "__main__":
    main()

