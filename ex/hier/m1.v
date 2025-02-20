module m1 (
    input wire a,
    input wire b,
    output wire [7:0] o
);

m2 m2a_inst(.a(a), .b(b), .o(o[3:0]));
m2 m2b_inst(.a(a), .b(b), .o(o[7:4]));

endmodule