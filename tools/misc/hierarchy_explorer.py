import os
import xml.etree.ElementTree as ET


def extract_module_hierarchy(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    def parse_hierarchy(cell_element):
        hierarchy = {
            "name": cell_element.get("name"),
            "submodname": cell_element.get("submodname"),
            "hier": cell_element.get("hier"),
            "children": []
        }
        for child in cell_element.findall("cell"):
            hierarchy["children"].append(parse_hierarchy(child))
        return hierarchy
    
    hierarchy_list = []
    for cell in root.findall(".//cell"):
        if '.' not in cell.get("hier", ""):  # Find top-level modules
            hierarchy_list.append(parse_hierarchy(cell))
    
    return hierarchy_list


def get_hierarcy(flist, xml_file='hierarchy.xml'):
    # Check if verilator is installed
    if os.system('which verilator') != 0:
        print("Verilator is not installed. Please install it first.")
        return
    # Get hierarchy from verilator
    cmd = f'verilator --xml-only --xml-output {xml_file}'
    if 'topmodule' in flist and flist['topmodule'] is not None:
        cmd += f' --top-module {flist["topmodule"]}'
    for d in flist['incdirs']:
        cmd += f' -I{d}'
    for d in flist['defines']:
        cmd += f' -D{d}'
    for f in flist['files']:
        cmd += f' {f}'
    os.system(cmd)


def parse_hierarchy(node, dot_lines, parent=None):
    """ Recursively parse the hierarchy dictionary and add nodes/edges to the DOT lines. """
    node_id = node["hier"]  # Use the full hierarchy path as the unique node ID
    label = f'{node["name"]}\\n({node["submodname"]})'  # Format: instance_name (module_name)
    
    dot_lines.append(f'    "{node_id}" [label="{label}", shape="box", style="filled", fillcolor="lightblue"];')
    
    if parent:
        dot_lines.append(f'    "{parent}" -> "{node_id}";')
    
    for child in node.get("children", []):
        parse_hierarchy(child, dot_lines, node_id)


def parse_hierarchy_nested(node, dot_lines):
    """ Recursively parse the hierarchy dictionary and add nodes/edges to the DOT lines in a nested format. """
    node_id = node["hier"]  # Use the full hierarchy path as the unique node ID
    label = f'{node["name"]}\\n({node["submodname"]})'  # Format: instance_name (module_name)
    
    dot_lines.append(f'    subgraph "cluster_{node_id}" {{')
    dot_lines.append(f'        label="{label}";')
    dot_lines.append(f'        style="filled";')
    dot_lines.append(f'        fillcolor="lightblue";')
    
    for child in node.get("children", []):
        child_id = child["hier"]
        child_label = f'{child["name"]}\\n({child["submodname"]})'
        dot_lines.append(f'        "{child_id}" [label="{child_label}", shape="box", style="filled", fillcolor="lightblue"];')
        parse_hierarchy_nested(child, dot_lines)
    
    dot_lines.append('    }')


def generate_graphviz(hierarchy, output_file, nested=False):
    """ Generate a Graphviz diagram from the hierarchical module list. """
    dot_lines = ['digraph G {', '    rankdir=TB;']  # Top to bottom layout
    
    if nested:
        for root in hierarchy:
            parse_hierarchy_nested(root, dot_lines)
    else:
        for root in hierarchy:
            parse_hierarchy(root, dot_lines)
    
    dot_lines.append('}')
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(dot_lines))
    
    print(f"Graph saved as {output_file}")


def print_hierarchy(hierarchy):
    def print_hierarchy_recursive(node, indent=0, is_last=True):
        prefix = "    " * (indent - 1) + ("└── " if is_last else "├── ") if indent > 0 else ""
        print(f'{prefix}{node["name"]} ({node["submodname"]})')
        children = node.get("children", [])
        for i, child in enumerate(children):
            print_hierarchy_recursive(child, indent + 1, i == len(children) - 1)
    
    for root in hierarchy:
        print_hierarchy_recursive(root)


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Json filelist')
    parser.add_argument('-o', '--output', help='Output file', default='hierarchy.dot')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-p', '--print', help='Print hierarchy', action='store_true')
    parser.add_argument('-n', '--nested', help='Print as nested modules', action='store_true')
    args = parser.parse_args()

    flist = None
    with open(args.file, 'r') as f:
        flist = json.load(f)
    
    # Generate xml using verilator
    get_hierarcy(flist, '/tmp/hierarchy.xml')

    # Parse the hierarchy xml
    hier = extract_module_hierarchy('/tmp/hierarchy.xml')

    if args.print:
        print_hierarchy(hier)
    else:
        # Generate the Graphviz diagram
        generate_graphviz(hier, args.output, nested=args.nested)
