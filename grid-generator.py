#!/usr/bin/python3

import operator
import random
import sys

from functools import reduce

from pylatex import Document, MiniPage, VerticalSpace, Tabular, utils
from pylatex.basic import NewLine, NewPage
from pylatex.position import HorizontalSpace

def generate_grid(size:int ,empty: int, op: operator = operator.add):
    """generate a fubuki grid

    Args:
        size (int): size of a side of the fubuki grid
        empty (int): number of empty cells in the grid
    """
    # generate list of ints contained in the grid from 1 to size squared
    l = [x for x in range(1,(size**2)+1)]
    # shuffle them
    # sum(1 for _ in l): to get the length of l, but l is a generator so len() does not work
    shuffle = random.sample(l,sum(1 for _ in l))

    # calculate solution
    res_lines = []
    res_collumns = []
    for index in range(size):
        res_lines.append(reduce( lambda a, b: op(a,b), [shuffle[i] for i in range(len(shuffle)) if int(i/size) == index]))
        res_collumns.append(reduce( lambda a, b: op(a,b), [shuffle[i] for i in range(len(shuffle)) if int(i%size) == index]))

    # filter which cells will be printed
    # create a conservator element filter
    selector = random.sample([1] * (size**2 - empty) + [0] * empty, size**2)
    # select which will be displayed
    selected_shuffle = [shuffle[i] * selector[i] for i in range(size**2)]
    # split all results into lines for the fubuki square format
    lines = [selected_shuffle[i:i+size] + [res_lines[int(i/size)]] for i in range(0,len(selected_shuffle), size)]
    lines.append(res_collumns + [0])
    return lines

def usage():
        print(f"usage:\n\tgrid-generator.py <size#> <empty#>")
        print("\t<size#> must be positive, and <empty#> positive and inferior to <size#> squared")
        print("\nvalid example:\n")
        print("\tpython3 grid-generator.py 3 5")
        print("\ninvalid example:\n")
        print("\tpython3 grid-generator.py 3 10 (10 > 3x3)\n")
        exit(1)

if __name__ == "__main__":
    # validate entries
    if len(sys.argv) < 4:
        usage()

    size = int(sys.argv[1])
    empty = int(sys.argv[2])
    count = int(sys.argv[3])

    op_name = "add"
    if len(sys.argv) > 4:
        if sys.argv[4] == "mul":
            op_name = sys.argv[4]

    op = operator.mul if len(sys.argv) > 4 and sys.argv[4] == "mul" else operator.add

    if (size < 0) or (empty < 0 or empty > size**2):
        usage()

    # create pdf with the help of pylatex
    geometry_options = {"left": "10mm", "right": "20mm", "top": "15mm", "bottom": "0mm"}
    doc = Document(geometry_options=geometry_options)

    doc.change_document_style("empty")
    for i in range(count):
        if (i % (7-size)) != 0:
            doc.append(HorizontalSpace(r"5.5mm"))

        with doc.create(
            MiniPage(width=r"0.5\textwidth", height=r"0.5\textwidth", fontsize="Huge")):
            with doc.create(Tabular("|c"*size + "||c|")) as Table:
                Table.add_hline()
                lines = generate_grid(size, empty, op)
                for line in lines:
                    output = [f"{item:3}" if item != 0 else "__" for item in line]
                    boldified = utils.bold(output[-1])
                    output[-1] = boldified
                    Table.add_row(output if line != lines[-1] else [utils.bold(elem) for elem in output[:-1]] + [" "])
                    Table.add_hline()
                    if line == lines[-2]:
                        Table.add_hline()

        doc.append(VerticalSpace(f"16mm"))
        doc.append(NewLine())

        if (i % (7-size)) == (7-size) - 1:
             doc.append(NewPage())

    doc.generate_pdf(f"fubuki_{op_name}_{size}x{size}_{count}", clean_tex=True)



