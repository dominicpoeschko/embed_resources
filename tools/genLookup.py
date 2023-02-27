#!/usr/bin/env python

import os, os.path, argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Embedded content generator")
    parser.add_argument('--output', '-o', action='store', dest='output', type=str, help='Output', required=True)
    parser.add_argument('--namespace', '-s', action='store', dest='namespace', type=str, help='Namespace', required=True)
    parser.add_argument('--input', '-p', action='store', dest='input_files',  type=str,nargs='*', help='Input files', required=True)
    return parser.parse_args()

def make_c_identifier(name):
    return name.replace("\\","/").replace("/","_").replace(".","_").replace("-","_")

def main():
    args = parse_arguments()
    with open(args.output+".hpp", 'w') as output_header:
        output_header.write("#pragma once\n")
        output_header.write("#include <span>\n")
        output_header.write("#include <cstddef>\n")
        output_header.write("#include <optional>\n")
        output_header.write("#include <string_view>\n")
        output_header.write("namespace embed_resources {\n")
        output_header.write("namespace ")
        output_header.write(args.namespace)
        output_header.write("{\n")
        output_header.write("    std::optional<std::span<std::byte const>> get_resource(std::string_view path);\n")
        output_header.write("}}\n")
    with open(args.output+".cpp", 'w') as output_source:
        output_source.write("#include \"")
        output_source.write(os.path.basename(args.output))
        output_source.write(".hpp\"\n")
        output_source.write("namespace embed_resources {\n")
        output_source.write("namespace ")
        output_source.write(args.namespace)
        output_source.write("{\n")
        for f_name in args.input_files:
            output_source.write("    extern std::span<std::byte const> const ")
            output_source.write(make_c_identifier(f_name))
            output_source.write(";\n")
        output_source.write("    std::optional<std::span<std::byte const>> get_resource(std::string_view path){\n")

        for f_name in args.input_files:
            output_source.write("        if(path == \"")
            output_source.write(f_name)
            output_source.write("\") {\n")
            output_source.write("            return ")
            output_source.write(make_c_identifier(f_name))
            output_source.write(";\n        }\n")

        output_source.write("        return std::nullopt;\n")
        output_source.write("    }\n")
        output_source.write("}}\n")

if __name__ == '__main__':
    main()


