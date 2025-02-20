# hwtools
A toolbox for hardware design



## `genflist`: A tool to generate file lists.
```bash
# Example Usage
genflist -v -r <proj_dir> -o project.f          # Generate filelist in txt format
genflist -v -r <proj_dir> -o project.f -f json  # Generate filelist in json format
```

## `hierviz`: A tool to visualize verilog module hierarchy
```bash
# Example Usage
hierviz mymodule.v                      # Print hierarchy
hierviz mymodule.v -f filelist.f -d 2   # Print hierarchy (till depth=2)
hierviz mymodule.v --dot mymodule.dot   # Export dot graph
```
