#! /usr/bin/env python
################################################################################
# A tool to generate a file list for project to be used by other tools
################################################################################
import os

def gen_flist(dirs, output_file, cwd='.', exts=[], ignoredirs=[], defines=[], include_dirs=[], recursive=False, sort=True, verbose=True):
    includes = [f'+incdir+{d}' for d in include_dirs]
    defines = [f'+define+{d}' for d in defines] 
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

    return includes + [''] + defines + [''] + flist


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate file list for VLSI tools")
    parser.add_argument("dir", help="Root directory of the project", nargs="+")
    parser.add_argument("-i", "--ignore", help="Ignore directory", default="build", nargs="*")
    parser.add_argument("-I", "--include", help="Specify include dirs for file list", nargs="*")
    parser.add_argument("-D", "--define", help="Specify macros for file list", nargs="*")
    parser.add_argument("-e", "--ext", help="File extension to search (comma separated)", default="v,sv")
    parser.add_argument("-C", "--change-dir", help="Change to directory before searching")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-r", "--recursive", help="Recursive search", action="store_true")
    parser.add_argument("-s", "--sort", help="Sort the file list", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    args = parser.parse_args()

    exts = args.ext.split(",")
    exts = [f".{ext}" for ext in exts]

    incdirs = args.include if args.include else []
    ignoredirs = args.ignore if args.ignore else []
    defines = args.define if args.define else []

    if args.verbose:
        print("Root        :", args.dir)
        print("Output      :", args.output)
        print("Include Dirs:", incdirs)
        print("Ignore Dirs :", ignoredirs)
        print("File Ext    :", exts)
        print("Defines     :", defines)

    flist = gen_flist(args.dir, args.output, cwd=args.change_dir, exts=exts, ignoredirs=ignoredirs, defines=defines, 
                      include_dirs=incdirs, recursive=args.recursive, sort=args.sort, verbose=args.verbose)

    nfiles = len(flist)
    print(f"Found {nfiles} files")

    if args.output:
        print(f"Writing file: {args.output}")
        with open(args.output, 'w') as f:
            f.write('#'*80 + '\n')
            f.write(f"# File list for project in {args.dir}\n")
            f.write('#'*80 + '\n')
            f.write('\n'.join(flist))
    else:
        print('\n'.join(flist))