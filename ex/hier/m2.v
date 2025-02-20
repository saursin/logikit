module m2 (
    input wire a,
    input wire b,
    output wire [3:0] o
);

m3 m3a_inst(.a(a), .b(b), .o(o[1:0]));
m3 m3b_inst(.a(a), .b(b), .o(o[3:2]));

endmodule