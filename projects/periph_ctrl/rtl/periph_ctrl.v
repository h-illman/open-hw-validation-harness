// periph_ctrl.v
// A simple register-mapped peripheral controller.
//
// This is the Phase 3 MVP DUT.  It is representative of the kind of
// memory-mapped peripheral block found on real FPGAs and SoCs:
// a small address-decoded register file with read-only, read-write,
// and status registers, a GPIO output, and clean error signaling.
//
// Register map  (addr[2:0]):
// ┌──────┬────────────┬────────┬───────┬────────────────────────────────┐
// │ Addr │ Name       │ Access │ Reset │ Description                    │
// ├──────┼────────────┼────────┼───────┼────────────────────────────────┤
// │ 0x0  │ REG_ID     │ RO     │ 0xAB  │ Peripheral ID constant         │
// │ 0x1  │ REG_GPIO   │ RW     │ 0x00  │ GPIO output register           │
// │ 0x2  │ REG_CTRL   │ RW     │ 0x00  │ Control register               │
// │ 0x3  │ REG_STATUS │ RO     │ –     │ {6'b0, ctrl_en, gpio_nonzero} │
// │ 0x4+ │ –          │ –      │ –     │ Invalid — asserts addr_err     │
// └──────┴────────────┴────────┴───────┴────────────────────────────────┘
//
// REG_STATUS fields:
//   bit 0 : gpio_nonzero — 1 if any GPIO output bit is high
//   bit 1 : ctrl_en      — mirrors bit 0 of REG_CTRL
//   bits 7:2 : reserved, always 0
//
// Timing:
//   All outputs (rd_data, rd_valid, addr_err) are registered.
//   They update on the rising edge following a valid rd_en or wr_en pulse.
//   addr_err pulses for exactly one cycle on an invalid-address access.
//
// Writes to read-only registers (REG_ID, REG_STATUS) are silently ignored.

`timescale 1ns/1ps

module periph_ctrl (
    input  wire       clk,
    input  wire       rst_n,

    // Register bus
    input  wire [2:0] addr,       // register address (0-3 valid, 4-7 invalid)
    input  wire       wr_en,      // write enable (pulse high for one cycle)
    input  wire       rd_en,      // read enable  (pulse high for one cycle)
    input  wire [7:0] wr_data,    // write data

    output reg  [7:0] rd_data,    // read data (valid when rd_valid=1)
    output reg        rd_valid,   // 1 for the cycle after a valid read
    output reg        addr_err,   // 1 for the cycle after an invalid address

    // GPIO
    output wire [7:0] gpio_out    // live value of REG_GPIO
);

    // -----------------------------------------------------------------------
    // Address constants
    // -----------------------------------------------------------------------
    localparam [2:0] ADDR_ID     = 3'h0;
    localparam [2:0] ADDR_GPIO   = 3'h1;
    localparam [2:0] ADDR_CTRL   = 3'h2;
    localparam [2:0] ADDR_STATUS = 3'h3;
    localparam [7:0] PERIPHERAL_ID = 8'hAB;

    // -----------------------------------------------------------------------
    // Internal registers
    // -----------------------------------------------------------------------
    reg [7:0] reg_gpio;   // RW: drives gpio_out
    reg [7:0] reg_ctrl;   // RW: general control bits

    // -----------------------------------------------------------------------
    // Combinational derived signals
    // -----------------------------------------------------------------------
    wire addr_valid  = (addr <= 3'h3);

    // REG_STATUS is computed from current register state, not stored
    wire [7:0] reg_status = {6'b00_0000, reg_ctrl[0], |reg_gpio};

    // GPIO output is the live register value (no extra latency)
    assign gpio_out = reg_gpio;

    // -----------------------------------------------------------------------
    // Write path  (synchronous, active-low reset)
    // Writes to RO registers are silently ignored — standard peripheral behavior.
    // -----------------------------------------------------------------------
    always @(posedge clk) begin
        if (!rst_n) begin
            reg_gpio <= 8'h00;
            reg_ctrl <= 8'h00;
        end else if (wr_en && addr_valid) begin
            case (addr)
                ADDR_GPIO:   reg_gpio <= wr_data;
                ADDR_CTRL:   reg_ctrl <= wr_data;
                default: ;   // ADDR_ID and ADDR_STATUS: writes silently ignored
            endcase
        end
    end

    // -----------------------------------------------------------------------
    // Read path + error signaling  (synchronous)
    // rd_valid and addr_err are mutually exclusive; both clear when idle.
    // -----------------------------------------------------------------------
    always @(posedge clk) begin
        if (!rst_n) begin
            rd_data  <= 8'h00;
            rd_valid <= 1'b0;
            addr_err <= 1'b0;
        end else begin
            // Default: clear strobes each cycle (pulsed, not sticky)
            rd_valid <= 1'b0;
            addr_err <= 1'b0;

            if (rd_en || wr_en) begin
                if (!addr_valid) begin
                    // Invalid address on any access type
                    addr_err <= 1'b1;
                end else if (rd_en) begin
                    // Valid read
                    rd_valid <= 1'b1;
                    case (addr)
                        ADDR_ID:     rd_data <= PERIPHERAL_ID;
                        ADDR_GPIO:   rd_data <= reg_gpio;
                        ADDR_CTRL:   rd_data <= reg_ctrl;
                        ADDR_STATUS: rd_data <= reg_status;
                        default:     rd_data <= 8'hFF; // unreachable
                    endcase
                end
                // wr_en with valid addr: write happens silently, no rd_valid
            end
        end
    end

endmodule
