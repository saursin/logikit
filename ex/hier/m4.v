`include "common.vh"

module m4 (
    input wire a,
    input wire b,
    output wire o
);
    `UNUSED_VAR(b)
    assign o = a;

endmodule