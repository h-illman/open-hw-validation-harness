// reg8.v
// 8-bit registered with synchronous load and active-low reset.
//
// Ports:
//   clk    - clock input
//   rst_n  - active-low synchronous reset
//   en     - load enable (1 = load d into q, 0 = hold q)
//   d      - 8-bit data input
//   q      - 8-bit registered output
//
// Behavior:
//   On every rising edge of clk:
//     If rst_n == 0  ->  q <= 0
//     Else if en == 1 ->  q <= d
//     Else            ->  q holds current value
//
// This module is the Phase 2 bring-up DUT.
// It is intentionally simple so the focus stays on the validation harness.

`timescale 1ns/1ps

module reg8 (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    input  wire [7:0] d,
    output reg  [7:0] q
);

    always @(posedge clk) begin
        if (!rst_n)
            q <= 8'h00;
        else if (en)
            q <= d;
        // else: q holds its current value (implicit register behaviour)
    end

endmodule
