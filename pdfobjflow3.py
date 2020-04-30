#!/usr/bin/env python3

"""
AUTHOR:
  Sebastien Damaye (aldeid.com)

VERSION:
  1.1

UPDATED:
  2014-01-22 - Added pydot import to automatically generate png output
  2014-01-17 - Initial release

DESCRIPTION:
  This program is meant to be used with pdf-parser from Didier Stevens.
  It reads the output from pdf-parser and creates the map of the objects flows
  under the form of a DOT file. You can then use the dot utility to export an
  image (e.g. PNG file)

USAGE:
  $ ./pdf-parser pdf.pdf | ./pdfobjflow3.py -
"""
import io
import os
import re
import sys
from typing import List

try:
    import pydot
except:
    print("You must install pydot:")
    print("  sudo aptitude install python-pydot")
    print("or,")
    print("https://www.graphviz.org/")
    sys.exit()


def convert_pdf_output_file_to_dotfile(pdf_output_path: str, dot_path: str) -> None:
    """
    :param pdf_output_path: Path of file containing PDF output data
    :param dot_path: Path to dotfile
    :return:
    """
    with open(pdf_output_path, 'r') as file:
        il = file.readlines()

    with open(dot_path, 'w') as file:
        for line in pdf_output_to_dotfile_output(il):
            file.write(line)


def convert_pdf_output_list_to_dotfile(pdf_output_list: List[str], dot_path: str) -> None:
    """
    :param pdf_output_list: List of lines of PDF output
    :param dot_path: Path to save dot file to
    :return:
    """
    with open(dot_path, 'w') as file:
        for line in pdf_output_to_dotfile_output(pdf_output_list):
            file.write(line)


def pdf_output_to_dotfile_output(pdf_data: List[str]) -> List[str]:
    """
    :param pdf_data: List of PDF output lines.
    :return: List of .dot graph file lines.
    """
    o = ["digraph G {"]

    for l in pdf_data:
        m1 = re.match(r"obj (\w+) (\w+)", l)
        m2 = re.match(r" Referencing: (.*)", l)
        if m1:
            obj = '%s.%s' % m1.group(1, 2)
        if m2:
            ref = filter(None, m2.group(1).split(", "))
            ref = [x for x in ref]
            if len(ref) == 0:
                o.append("\"%s\";\n" % obj)
            else:
                for r in ref:
                    o.append("\"%s\"->\"%s\";\n" % (obj, r.replace(" ", ".").replace(".R", "")))

    o.append("}")

    return o


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", default=None,
                        help="Filepath to read PDF output from. "
                             "If this is not set, we read from stdin.")
    parser.add_argument("--outputfilename", default='pdfobjflow3',
                        help="The name of the .dot and .png file to output.")
    parser.add_argument("--outputfolder", default='out',
                        help="The folder to save files to.")

    args = parser.parse_args()

    OUTPUT_FILENAME = args.outputfilename
    OUTPUT_FOLDER = args.outputfolder
    INPUT_PDF_DATA_FILE = args.inputfile
    STDIN = False  # assume we are reading from a file and not stdin

    if INPUT_PDF_DATA_FILE is None:
        STDIN = True

    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    if STDIN:
        convert_pdf_output_list_to_dotfile(sys.stdin.readlines(),
                                           os.path.join(OUTPUT_FOLDER, "pdfobjflow.dot"))
    else:
        convert_pdf_output_file_to_dotfile(INPUT_PDF_DATA_FILE,
                                           os.path.join(OUTPUT_FOLDER, "pdfobjflow.dot"))

    graph = pydot.graph_from_dot_file(os.path.join(OUTPUT_FOLDER, "pdfobjflow.dot"))[0]  # unpack list
    graph.write_png(os.path.join(OUTPUT_FOLDER, "pdfobjflow.png"))
