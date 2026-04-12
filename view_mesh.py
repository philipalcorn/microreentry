import argparse

import drawing
from config import Config
from drawing import print_sheet
from topology import build_sheet


def _disable_colors():
    drawing.RESET = ""
    drawing.MUSCLE_REFRACTORY = ""
    drawing.MUSCLE_READY = ""
    drawing.MUSCLE_CONDUCTING = ""
    drawing.NODE_IDLE = ""
    drawing.NODE_FIRED = ""
    drawing.MUSCLE_MARKED = ""
    drawing.BAR_READY = ""
    drawing.BAR_REFRACTORY = ""


def main(argv=None):
    cfg = Config()

    parser = argparse.ArgumentParser(
        description="Build and print a static mesh with node and muscle IDs"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=cfg.length,
        help="Sheet size (creates (length+1)x(length+1) nodes)",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable ANSI colors for plain-text output",
    )

    args = parser.parse_args(argv)

    if args.plain:
        _disable_colors()

    nodes, muscles = build_sheet(args.length)

    print(f"Mesh length: {args.length}")
    print(f"Nodes: {len(nodes)} (IDs 0..{len(nodes) - 1})")
    print(f"Muscles: {len(muscles)} (IDs 0..{len(muscles) - 1})")
    print()
    print_sheet(args.length, nodes, muscles)


if __name__ == "__main__":
    main()
