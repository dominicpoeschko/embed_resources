#!/usr/bin/env python

import os, os.path, argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Embedded content generator")
    parser.add_argument('--output', '-o', action='store', dest='output_file', type=str, help='Output File', required=True)
    parser.add_argument('--input', '-i', action='store', dest='input_file', type=str, help='Input File', required=True)
    parser.add_argument('--namespace', '-s', action='store', dest='namespace', type=str, help='namespace', required=True)
    parser.add_argument('--name', '-n', action='store', dest='name', type=str, help='name', required=True)
    return parser.parse_args()

def create_file_entry_byte(file_bytes):
    output = []
    for start in range(0, len(file_bytes), 16):
        output.append("        " + "".join("'\\x{:02x}',".format(x) for x in file_bytes[start:start+16]) + "\n")
    return ''.join(output)

def main():
    args = parse_arguments()

    with open(args.input_file, 'rb') as input_file:
        file_bytes = input_file.read()
        entry =  create_file_entry_byte(file_bytes)
        os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
        with open(args.output_file, 'w') as output_file:
            output_file.write("#include <array>\n")
            output_file.write("#include <span>\n")
            output_file.write("#include <cstddef>\n")
            output_file.write("#ifdef __clang__\n")
            output_file.write("    #pragma clang diagnostic push\n")
            output_file.write("    #pragma clang diagnostic ignored \"-Wglobal-constructors\"\n")
            output_file.write("#endif\n")
            output_file.write("namespace embed_resources {\n")
            output_file.write("namespace ")
            output_file.write(args.namespace)
            output_file.write("{\nnamespace detail{\n")
            output_file.write("    constexpr std::array<char, ")
            output_file.write(str(len(file_bytes)))
            output_file.write("> ")
            output_file.write(args.name)
            output_file.write("{\n")
            output_file.write(entry)
            output_file.write("    };\n}\n")
            output_file.write("    extern std::span<std::byte const> const ")
            output_file.write(args.name)
            output_file.write(";\n")
            output_file.write("    extern std::span<std::byte const> const ")
            output_file.write(args.name)
            output_file.write(" = std::as_bytes(std::span{detail::")
            output_file.write(args.name)
            output_file.write("});\n")
            output_file.write("}}\n")
            output_file.write("#ifdef __clang__\n")
            output_file.write("    #pragma clang diagnostic pop\n")
            output_file.write("#endif\n")

if __name__ == '__main__':
    main()
