import pymupdf as fitz

def parse_selection_ranges(selection: str, page_count: int) -> list[tuple[int, int]]:
    # i.e. [(1, 100), (2, 100)]
    selection = selection.strip()
    if not selection:
        return []
    if selection.lower() == "all":
        return [(0, page_count)]
    parts = [ part.strip() for part in selection.split(",") ]
    result = []
    for part in parts:
        if "-" in part:
            range_parts = part.split("-")
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range {part}")
            rbegin = int(range_parts[0])
            rend   = int(range_parts[1]) if len(range_parts[1]) > 0 else page_count
            if rbegin > rend:
                rbegin, rend = rend, rbegin
            if rend > page_count:
                rend = page_count
            if rbegin > rend:
                continue
            result.append((rbegin-1, rend))
        else:
            part = int(part)-1
            result.append((part, part))
    return result

def shiftargs(args: list[str], errmsg: str) -> tuple[str, list[str]]:
    if len(args) == 0:
        print(f"ERROR: {errmsg}")
        exit(-1)
    return args[0], args[1:]

def parse_ops(args: list[str]) -> list[list[str]]:
    ops = []
    while len(args) > 0:
        arg, args = shiftargs(args, "Unreachable")
        match arg:
            case "-i":
                input_filepath, args = shiftargs(args, "Provide an input filepath after the -i flag")
                op = [ "-i", input_filepath ]
                while len(args) > 0 and not args[0].startswith("-"):
                    selection, args = shiftargs(args, "Unreachable")
                    op.append(selection)
                ops.append(op)
            case "-o":
                output_filepath, args = shiftargs(args, "Provide an output filepath after the -o flag")
                ops.append([ "-o", output_filepath ])
            case "-h":
                print("pdfarrange.py")
                exit(0)
    return ops

def parse_args(source: str) -> list[str]:
    args = []
    i = 0
    n = len(source)

    while i < n:
        # skip whitespace
        while i < n and source[i].isspace():
            i += 1
        if i >= n:
            break

        # quoted argument
        if source[i] == '"':
            i += 1
            start = i
            while i < n and source[i] != '"':
                i += 1
            if i >= n:
                raise ValueError("Unterminated quote")
            args.append(source[start:i])
            i += 1  # skip closing quote
        else:
            # unquoted argument
            start = i
            while i < n and not source[i].isspace():
                i += 1
            args.append(source[start:i])

    return args

if __name__ == "__main__":
    # pdfarrange.py -i source.pdf 10-100 20-100 -o output.pdf
    import sys
    _, args = shiftargs(sys.argv, "Unreachable")
    ops = []
    DEBUG_MODE = False
    while len(args) > 0:
        arg, args = shiftargs(args, "Unreachable")
        match arg:
            case "-debug":
                DEBUG_MODE = True
            case "-R":
                sourcefp, args = shiftargs(args, "Provide a source file to execute")
                with open(sourcefp, "r") as file:
                    source_args = parse_args(file.read().strip())
                    ops.extend(parse_ops(source_args))
            case "-i":
                input_filepath, args = shiftargs(args, "Provide an input filepath after the -i flag")
                op = [ "-i", input_filepath ]
                while len(args) > 0 and not args[0].startswith("-"):
                    selection, args = shiftargs(args, "Unreachable")
                    op.append(selection)
                ops.append(op)
            case "-o":
                output_filepath, args = shiftargs(args, "Provide an output filepath after the -o flag")
                ops.append([ "-o", output_filepath ])
            case "-h":
                print("pdfarrange.py")
                exit(0)

    read_op_start = 0
    for ip, op in enumerate(ops):
        if op[0] != "-o":
            continue
        if read_op_start == ip:
            print(f"WARNING: trying to generate empty PDF file. This operations '{op[0]} {op[1]}' is skipped")
            print(f"WARNING: {read_op_start} {ip}")
            continue

        opcode, output_filepath = op[0], op[1]
        with fitz.open() as output_doc:
            print(f"INFO: generating {output_filepath}")
            input_amount = ip - read_op_start 
            for i in range(input_amount):
                current_read_op_index = read_op_start + i
                current_read_op = ops[current_read_op_index]
                op, input_filepath, selections = current_read_op[0], current_read_op[1], current_read_op[2:]
                with fitz.open(input_filepath) as input_doc:
                    pages_to_read = []
                    if len(selections) == 0:
                        print("WARNING: empty selection")
                        continue
                    for selection in selections:
                        ranges = parse_selection_ranges(selection, input_doc.page_count)
                        for begin, end in ranges:
                            if begin != end:
                                end -= 1
                            output_doc.insert_pdf(input_doc, from_page=begin, to_page=end)
            if not DEBUG_MODE:
                output_doc.save(
                        output_filepath,
                        garbage=4,        # remove unused objects aggressively
                        deflate=True,     # compress all streams
                        clean=True,       # rebuild xref tables
                        incremental=False,# rewrite whole file
                        )
        read_op_start = ip + 1
