import argparse
import os


def existing_file_arg_type(path: str) -> str:
    if os.path.isfile(path):
        return path

    if os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"expected {path} to be a file, but is a dir instead")

    raise argparse.ArgumentTypeError(f"could not find {path}")


def existing_dir_arg_type(path: str) -> str:
    if os.path.isdir(path):
        return path.removeprefix(f".{os.path.sep}").removesuffix(os.path.sep)

    if os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"expected {path} to be a dir, but is a file instead")

    raise argparse.ArgumentTypeError(f"could not find {path}")
