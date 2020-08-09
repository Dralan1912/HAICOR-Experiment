"""
Copyright (c) 2020 Hecong Wang

This software is released under the MIT License.
https://opensource.org/licenses/MIT
"""
from __future__ import annotations

import argparse
import os.path
import pickle

from . import experiment


def load_subcommand(filename: str, directory: str, output: str):
    experiments = experiment.load_experiments(
        os.path.abspath(filename),
        os.path.abspath(directory)
    )

    with open(os.path.abspath(output), "wb") as file:
        pickle.dump(experiments, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    load_parser = subparsers.add_parser("load", help="Load experiment data")

    load_parser.add_argument("LOG", help="Experiment's log file.")
    load_parser.add_argument("DIR", help="Experiment's output directory.")
    load_parser.add_argument("OUT", help="Output pickle file.")

    args = parser.parse_args()

    if args.subcommand == "load":
        load_subcommand(args.LOG, args.DIR, args.OUT)
