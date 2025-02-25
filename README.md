# LogiKit
A toolbox for hardware design and testing


## Prerequisites
```bash
git clone https://github.com/saursin/logikit.git
cd logikit
pip3 install -r requirements.txt

# Setup environment variables
cat sourceme >> ~/.bashrc
```

That's it, you should now be able to run the tools
```bash
logikit --version           # Check logikit version
```

## RTL Design/Verification Tools

### genflist: A tool to generate file lists.
```bash
# Example Usage
genflist -v -r <proj_dir> -o project.f          # Generate filelist in txt format
genflist -v -r <proj_dir> -o project.f -f json  # Generate filelist in json format
```

### hierviz: A tool to visualize verilog module hierarchy
```bash
# Example Usage
hierviz mymodule.v                      # Print hierarchy
hierviz mymodule.v -f filelist.f -d 2   # Print hierarchy (till depth=2)
hierviz mymodule.v --dot mymodule.dot   # Export dot graph
```

### hexviz: A tool to examine binary files
```bash
# Example Usage
hexviz file.bin             # Dumps contents as hex (similar to hexdump)
hexwiz file.bin -w 32       # group words together using -w option
```

### tbgen: A Verilog/Systemverilog Testbench generator
```bash
# Example usage
tbgen my_fancy_module.v -o my_fancy_tb.v
```


## Miscellaneous Tools

### jobman: A tool to launch and track multiple jobs in parallel
```bash
# Example usage
jobman -j4 commands.txt     # commands.txt contains bash commands (one-per-line)
```

