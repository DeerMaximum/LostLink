import argparse

def init_argparser():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Lost link ai file search"
    )

    parser.add_argument("--debug", action="store_true", required=False,
                        help="Enable debug mode"
                        )

    parser.add_argument("-b", "--background", action="store_true", required=False,
                            help="Watch for file changes with fs-hooks"
                        )
    return parser