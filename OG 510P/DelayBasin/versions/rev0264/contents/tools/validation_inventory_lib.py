import pathlib

from validation_toolchain_lib import build_validation_toolchain


def ordered_validation_tools(root: pathlib.Path) -> list[str]:
    return build_validation_toolchain(root)
