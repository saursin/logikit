import os
import re
import argparse

def parse_verilog_file(file_path):
    verilog_code = ''
    try:
        with open(file_path, 'r') as f:
            verilog_code = f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        exit(1)


    # Updated regex for module name (handles parameters, newlines, and spacing variations)
    module_pattern = re.compile(
        r'module\s+(?P<module_name>\w+)'  # Capture module name
        r'(?:\s*#\s*\([^)]*\))?'          # Optionally match parameter list #( ... )
        r'\s*\('                          # Match opening parenthesis (possibly on a new line)
    )

    # Regex for ports
    port_pattern = re.compile(
        r'(?P<direction>input|output)\s+'
        r'(?P<type>wire|reg)?\s*'
        r'(?:\[(?P<msb>\d+):(?P<lsb>\d+)\]\s*)?'
        r'(?P<name>\w+)'
    )

    # Extract module name
    module_match = module_pattern.search(verilog_code)
    module_name = module_match.group("module_name") if module_match else None

    # Extract ports
    ports = []
    for match in port_pattern.finditer(verilog_code):
        ports.append({
            "direction": match.group("direction"),
            "type": match.group("type") if match.group("type") else "wire",
            "msb": int(match.group("msb")) if match.group("msb") else None,
            "lsb": int(match.group("lsb")) if match.group("lsb") else None,
            "name": match.group("name")
        })

    return module_name, ports


def generate_testbench(module_name, ports):
    tb_name = f"{module_name}_tb"
    indent = "    "

    # Detect clock & reset ports
    clock_port = None
    reset_port = None
    reset_active_high = True  # Assume active-high unless name suggests otherwise

    def match_port_name(port_name, name_patterns):
        for name_pattern in name_patterns:
            if name_pattern in port_name.lower():
                return True
        return False

    for port in ports:
        if port["direction"] == "input" and port["msb"] is None:
            # Search for clock ports
            if not clock_port and match_port_name(port["name"], ["clk", "clock"]):
                clock_port = port["name"]
            
            # Search for reset ports
            if not reset_port and match_port_name(port["name"], ["rst", "reset"]):
                if 'n' in port["name"]:
                    reset_active_high = False
                reset_port = port["name"]


    # Header and timescale
    testbench = "// **** Testbench generated using tbgen *****\n\n"
    testbench += "`timescale 1ns / 1ps\n\n"
    testbench += f"module {tb_name};\n\n"

    # Signal declarations
    testbench += "    // Signal Declarations\n"
    for port in ports:
        direction = port["direction"]
        port_type = "reg" if direction == "input" else "wire"
        width = f"[{port['msb']}:{port['lsb']}] " if port["msb"] is not None else ""
        testbench += f"{indent}{port_type} {width}{port['name']};\n"

    testbench += "\n"

    # DUT instantiation
    testbench += "    // DUT Instantiation\n"
    testbench += f"{indent}{module_name} dut (\n"
    for i, port in enumerate(ports):
        comma = "," if i < len(ports) - 1 else ""
        testbench += f"{indent*2}.{port['name']}({port['name']}){comma}\n"
    testbench += f"{indent});\n\n"

    # Clock generation
    if clock_port:
        testbench += "    // Clock Generation\n"
        testbench += f"{indent}always #5 {clock_port} = ~{clock_port};\n\n"

    # Initial block for test sequences
    testbench += "    // Test Sequence\n"
    testbench += f"{indent}initial begin\n"
    testbench += f"{indent*2}$dumpfile(\"{tb_name}.vcd\");      // Generate VCD Waveform\n"
    testbench += f"{indent*2}$dumpvars(0, {tb_name});\n\n"

    if clock_port:
        print(f"Detected clock port: {clock_port}")
        testbench += f"{indent*2}{clock_port} = 0;\n"

    if reset_port:
        print(f"Detected reset port: {reset_port}")
        reset_value = "1" if reset_active_high else "0"
        release_value = "0" if reset_active_high else "1"
        testbench += f"{indent*2}{reset_port} = {reset_value};\n"
        testbench += f"{indent*2}repeat (10) @(posedge {clock_port});\n"
        testbench += f"{indent*2}{reset_port} = {release_value};\n\n"

    for port in ports:
        if port["direction"] == "input" and port["name"] != clock_port:
            if port["name"] in [clock_port, reset_port]:
                continue
            testbench += f"{indent*2}{port['name']} = 0;\n"

    testbench += f"\n{indent*2}// Add test sequences here\n"
    testbench += f"{indent*2}#10;\n"

    for port in ports:
        if port["direction"] == "input" and port["name"] != clock_port:
            testbench += f"{indent*2}{port['name']} = $random;\n"

    testbench += f"\n{indent*2}#100;\n"
    testbench += f"{indent*2}$finish;\n"
    testbench += f"{indent}end\n\n"

    # End module
    testbench += f"endmodule\n"

    return testbench


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a testbench for a Verilog/SystemVerilog module.')
    parser.add_argument('file', help='Verilog/SystemVerilog file')
    parser.add_argument('-o', '--output', help='Output directory')
    args = parser.parse_args()

    module_name, ports = parse_verilog_file(args.file)

    tb_content = generate_testbench(module_name, ports)
    tb_file = f"{module_name}_tb.v" if args.output is None else args.output
    with open(tb_file, 'w') as f:
        f.write(tb_content)
    print(f"Testbench for {module_name} generated at {tb_file}")