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
  $ ./pdf-parser pdf.pdf | ./pdfobjflow.py -
"""
import io
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


def pdf_output_to_graph_output(pdf_data: List[str]) -> List[str]:
    """
    :param pdf_data: List of PDF output lines.
    :return: List of .dot graph file lines.
    """
    o = ["digraph G {"]

    for l in f:
        m1 = re.match(r"obj (\w+) (\w+)", l)
        m2 = re.match(r" Referencing: (.*)", l)
        if m1:
            obj = "%s.%s" % m1.group(1, 2)
        if m2:
            ref = filter(None, m2.group(1).split(", "))
            ref = [x for x in ref]
            if len(ref) == 0:
                o.append("\"%s\";" % obj)
            else:
                for r in ref:
                    o.append("\"%s\"->\"%s\";" % (obj, r.replace(" ", ".").replace(".R", "")))

    o.append("}")

    return o


TEST = True
if TEST:
    with open('example_pdf_output.txt', 'r') as file:
        f = file.readlines()
else:
    f = sys.stdin.readlines()

o = open("pdfobjflow.dot", "w")

o.write("digraph G {\n")

for l in f:
    m1 = re.match(r"obj (\w+) (\w+)", l)
    m2 = re.match(r" Referencing: (.*)", l)
    if m1:
        obj = "%s.%s" % m1.group(1, 2)
    if m2:
        ref = filter(None, m2.group(1).split(", "))
        ref = [x for x in ref]
        if len(ref) == 0:
            o.write("\"%s\";\n" % obj)
        else:
            for r in ref:
                o.write("\"%s\"->\"%s\";\n" % (obj, r.replace(" ", ".").replace(".R", "")))

o.write("}")
o.close()

(graph,) = pydot.graph_from_dot_file('pdfobjflow.dot')  # tuple assignment thingy to avoid a list
graph.write_png('pdfobjflow.png')
