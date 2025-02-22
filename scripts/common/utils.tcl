# Function to get Verilog and SystemVerilog sources from file list
proc get_verilog_sources {file_list_file} {
    set file_list [split [read [open $file_list_file]] "\n"]
    set verilog_sources {}
    foreach file $file_list {
        if {[string match "*.v" $file] || [string match "*.sv" $file]} {
            lappend verilog_sources $file
        }
    }
    return $verilog_sources
}
