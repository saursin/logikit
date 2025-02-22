import sys

def print_tree(tree, getchild_callback, print_callback, max_depth=-1, prefix="", output=sys.stdout):
    """
    Print a tree structure with a custom print callback function.
    
    print_callback: A function that takes a node and returns a string to print
    getchild_callback: A function that takes a node and returns a list of child nodes.
    """
    def __print_hierarchy_recursive(node, prefix="", is_last=True, depth=0):
        if max_depth != -1 and depth > max_depth:
            return

        node_str = print_callback(node, depth)
        connector = "└── " if is_last else "├── "
        print(prefix + connector + node_str, file=output)

        child_prefix = prefix + ("    " if is_last else "│   ")
        instances = getchild_callback(node)

        for i, instance in enumerate(instances):
            __print_hierarchy_recursive(instance, child_prefix, i == len(instances) - 1, depth + 1)

    for i, root in enumerate(tree):
        __print_hierarchy_recursive(root, prefix, i == len(tree) - 1)


def simple_progress_bar(progress, bar_length=40):
    '''
    Returns a simple progress bar string
    '''
    fill_char = "▇"
    empty_char = " "
    block = int(round(bar_length * progress / 100))
    color_start = "\033[92m"  # Green color
    color_end = "\033[0m"     # Reset color
    colored_progress_bar = f"{color_start}{fill_char * block}{color_end}{empty_char * (bar_length - block)}"
    return f"|{colored_progress_bar}| {progress:.2f}%"
