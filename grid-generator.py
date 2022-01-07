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
        print(f"usage:\n\tgrid-generator.py <size#> <empty#> <grid_lines_count> [mul] [csv]")
        print("\t<size#> must be positive, and <empty#> positive and inferior to <size#> squared")
        print("\nvalid examples:\n")
        print("\tpython3 grid-generator.py 3 5 10")
        print("\tpython3 grid-generator.py 4 10 100 mul csv")
        print("\tpython3 grid-generator.py 3 3 1000 csv")
        print("\ninvalid example:\n")
        print("\tpython3 grid-generator.py 3 10 -1 (10 > 3x3) (-1 < 1)\n")
        exit(1)

if __name__ == "__main__":
    # validate entries
    if len(sys.argv) < 4:
        usage()

    size = int(sys.argv[1])
    empty = int(sys.argv[2])
    count = int(sys.argv[3])

    op_name = "add"
    csv_out = False

    if len(sys.argv) > 4:
        if sys.argv[4] == "mul":
            op_name = sys.argv[4]
        elif sys.argv[4] == "csv":
            csv_out = True

    if len(sys.argv) > 5 and sys.argv[5] == "csv":
        csv_out = True

    op = operator.mul if op_name == "mul" else operator.add

    if (size < 0) or (empty < 0 or empty > size**2) or (count < 1):
        usage()

    if csv_out:
        csv_data = []
        with open(f"fubuki_{op_name}_{size}x{size}_{count}.csv", "w") as f:
            for i in range(1, count+1):
                grid1 = generate_grid(size, empty, op)
                grid2 = generate_grid(size, empty, op)

                for line in zip(grid1,grid2):
                    l0 = [str(i) if i != 0 else "" for i in line[0]]
                    l1 = [str(i) if i != 0 else "" for i in line[1]]
                    f.write(f"{','.join(l0)},,,{','.join(l1)}\n")
                f.write(",\n"*2)

        exit(0)


    if size > 4:
        print("size superior to 4 are not supported in pdf format, use csv format instead")
        exit(1)

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



