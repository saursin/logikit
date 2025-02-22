################################################################################
# A TCL script to synthesize a design using Yosys
################################################################################
# Default settings
set filelist_file ""
set top_module ""
set output_dir "yosys_build"
set flatten 0
set fpga_vendor "xilinx"
set fpga_family "xc6s"
set build_dir "yosys_build"

################################################################################
# Parse command line arguments
set help_msg "Usage: yosys.tcl (options)\n\
 Options: \n\
  -f <file_list>        : Specify the file list \n\
  -top <module>         : Specify the top module \n\
  -out <dir>            : Specify the output directory (default: \$output_dir) \n\
  -flatten              : Flatten the design (default: \$flatten) \n\
  -vendor <fpga_vendor>      : Specify the FPGA vendor (default: \$fpga_vendor) \n\
  -family <fpga_family>      : Specify the FPGA family (default: \$fpga_family) \n\ 
  -build <dir>          : Specify the build directory (default: \$build_dir) \n\
  -help                 : Print this message  \n\
"

set argv [lassign $argv arg]
while {[llength $argv] > 0} {
    switch -- $arg {
        "-f" {
            set filelist_file [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-top" {
            set top_module [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-out" {
            set output_dir [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-flatten" {
            set flatten 1
        }
        "-vendor" {
            set fpga_vendor [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-family" {
            set fpga_family [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-build" {
            set build_dir [lindex $argv 0]
            set argv [lassign $argv arg]
        }
        "-help" {
            puts $help_msg
            exit 0
        }
        default {
            puts "Error: Unknown option $arg, try -help"
            exit 1
        }
    }
    set argv [lassign $argv arg]
}

################################################################################
# Check if file list is specified
if {$filelist_file == ""} {
    puts $help_msg
    puts "Error: No file list specified"
    exit 1
}

# Check if the top module is specified
if {$top_module == ""} {
    puts $help_msg
    puts "Error: Top module not specified"
    exit 1
}

################################################################################
# Output directories
set output_dir "$build_dir/output"
set report_dir "$build_dir/report"
file mkdir $output_dir
file mkdir $report_dir

# Source the utils.tcl file to use the get_verilog_sources function
source $env(HWTOOLS_ROOT)/scripts/common/utils.tcl

# Read the file list and get Verilog and SystemVerilog sources
set verilog_sources [get_verilog_sources $filelist_file]

################################################################################
# Read the design
yosys "echo on"

# Read Verilog
set rd_verilog_flags "-DSYNTHESIS_YOSYS"
foreach file $verilog_sources {
    yosys "read_verilog $rd_verilog_flags $file"
}

# Check hierarchy
yosys "hierarchy -check -top $top_module"

# Flatten
if {$flatten} {
    yosys "flatten"
}

# Check for problems
yosys "check -assert"

# Synthesize
yosys "synth_$fpga_vendor -family $fpga_family"

# Check for problems
yosys "check -assert"
# yosys "check -mapped"

# Write output files
yosys "write_json $output_dir/$top_module.json"
yosys "write_verilog $output_dir/$top_module.v"

# Write reports
yosys "tee -a $report_dir/utilization.rpt stat"
yosys "tee -a $report_dir/ltp.rpt ltp"
# yosys "tee -a $report_dir/timing.rpt sta"

# Cleanup
yosys "clean"

puts "----- We're done here -----"