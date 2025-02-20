#! /usr/bin/env python
################################################################################
# A tool to generate a file list for project to be used by other tools
################################################################################
import os

def gen_flist(dirs, output_file, cwd='.', exts=[], ignoredirs=[], recursive=False, sort=True, verbose=True):
    flist = []
    
    # expand dirs paths, remove duplicates
    dirs = [os.path.abspath(d) for d in dirs]
    dirs = list(set(dirs))

    # search for files
    for dir in dirs:
        # Walk through the directory
        for dirpath, dirnames, filenames in os.walk(dir):
            if verbose:
                print(f"> Searching dir: {dirpath}")
            if not recursive:
                dirnames.clear()
            for filename in filenames:
                if any(filename.endswith(ext) for ext in exts):
                    flist.append(os.path.join(dirpath, filename))
            for dirname in dirnames:
                if dirname in ignoredirs:
                    dirnames.remove(dirname)
                if dirname in incdirs:
                    for filename in os.listdir(os.path.join(dirpath, dirname)):
                        if any(filename.endswith(ext) for ext in exts):
                            flist.append(os.path.join(dirpath, dirname, filename))

    # calculate relative paths from cwd
    if cwd != '.':
        flist = [os.path.relpath(f, cwd) for f in flist]

    if sort:
        flist.sort()

    return flist


def write_json(output_file, flist, topmodule=None, defines=[], incdirs=[], verbose=True):
    import json
    flist = {
        "topmodule": topmodule,
        "defines": defines,
        "incdirs": incdirs,
        "files": flist
    }



    with open(output_file, 'w') as f:
        json.dump(flist, f, indent=4)


def write_flist(output_file, flist, topmodule=None, defines=[], incdirs=[], verbose=True):
    txt = '#'*80 + '\n'
    txt += f"# File list for project\n"
    txt += '#'*80 + '\n\n'
    txt += f'# Include directories\n'
    for d in incdirs:
        txt += f'+incdir+{d}\n'
    txt += '\n'
    txt += f'# Preprocessor Defines\n'
    for d in defines:
        txt += f'+define+{d}\n'
    txt += '\n'
    txt += '# Files\n'
    txt += '\n'.join(flist)

    with open(output_file, 'w') as f:
        f.write(txt)




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate file list for VLSI tools")
    parser.add_argument("dir", help="Root directories of the project", nargs="+")
    parser.add_argument("-i", "--ignore", help="Ignore directory", action="append")
    parser.add_argument("-I", "--include", help="Specify include dirs for file list", action="append")
    parser.add_argument("-D", "--define", help="Specify macros for file list", action="append")
    parser.add_argument("-t", "--topmodule", help="Top module name")
    parser.add_argument("-e", "--ext", help="File extension to search (comma separated)", default="v,sv")
    parser.add_argument("-C", "--change-dir", help="Change to directory before searching")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-f", "--output-format", help="Output format", default="flist", choices=["flist", "json"])
    parser.add_argument("-r", "--recursive", help="Recursive search", action="store_true")
    parser.add_argument("-s", "--sort", help="Sort the file list", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    args = parser.parse_args()

    verbose     = args.verbose
    incdirs     = args.include if args.include else []
    ignoredirs  = args.ignore if args.ignore else []
    defines     = args.define if args.define else []

    exts = args.ext.split(",")
    exts = [f".{ext}" for ext in exts]

    if args.verbose:
        print("Root dir     :", args.dir)
        print("Include dirs :", incdirs)
        print("Ignore dirs  :", ignoredirs)
        print("Defines      :", defines)
        print("File ext     :", exts)
        print("Output file  :", args.output)
        print("Output format:", args.output_format)
        print("Change dir   :", args.change_dir)

    # check if dirs exist
    def check_dir(dirs):
        for d in dirs:
            if not os.path.isdir(d):
                print(f"Error: Directory not found: {d}")
                exit(1)
    
    check_dir(args.dir)
    check_dir(incdirs)
    
    # convert to rel paths
    if args.change_dir != '.':
        incdirs = [os.path.relpath(f, args.change_dir) for f in incdirs]

    flist = gen_flist(args.dir, args.output, cwd=args.change_dir, exts=exts, ignoredirs=ignoredirs, recursive=args.recursive, sort=args.sort, verbose=args.verbose)

    nfiles = len(flist)
    print(f"Found {nfiles} files")

    output = args.output
    if not output:
        if args.output_format == "json":
            output = "proj.json"
        else:
            output = "proj.f"

    if args.verbose:
        print('Writing to file:', output)

    if args.output_format == "json":
        write_json(output, flist, topmodule=args.topmodule, defines=defines, incdirs=incdirs, verbose=args.verbose)
    else:
        write_flist(output, flist, topmodule=args.topmodule, defines=defines, incdirs=incdirs, verbose=args.verbose)