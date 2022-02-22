import argparse
import os


def existing_file_arg_type(path: str) -> str:
    if os.path.isfile(path):
        return path

    if os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"expected {path} to be a file, but is a dir instead")

    raise argparse.ArgumentTypeError(f"could not find {path}")
