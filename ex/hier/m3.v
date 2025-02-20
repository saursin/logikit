module m3 (
    input wire a,
    input wire b,
    output wire [1:0] o
);

m4 m4a_inst(.a(a), .b(b), .o(o[0]));
m4 m4b_inst(.a(a), .b(b), .o(o[1]));

endmodule