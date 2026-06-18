/**
 * File              : katan.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 24.09.2025
 * Last Modified Date: 24.09.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module katan #(
    parameter N = 32
) (
    input clk,
    input rst,
    output end_key_generation,
    input [79:0] key,
    input [N-1:0] block_i,
    output [N-1:0] block_o,
    input enc_dec,
    input rq_data,
    output end_signal
);

  assign end_key_generation = 1;


  logic [5:0] L1;
  logic [5:0] L2;
  logic [5:0] x1;
  logic [5:0] x2;
  logic [5:0] x3;
  logic [5:0] x4;
  logic [5:0] x5;
  logic [5:0] y1;
  logic [5:0] y2;
  logic [5:0] y3;
  logic [5:0] y4;
  logic [5:0] y5;
  logic [5:0] y6;

  katan_values #(
      .N(N)
  ) katan_values_impl (
      .L1(L1),
      .L2(L2),
      .x1(x1),
      .x2(x2),
      .x3(x3),
      .x4(x4),
      .x5(x5),
      .y1(y1),
      .y2(y2),
      .y3(y3),
      .y4(y4),
      .y5(y5),
      .y6(y6)
  );


  logic key_lfsr_shift;
  logic key_lfsr_rst;
  logic [79:0] key_lfsr_state;

  LFSR #(
      .DATA_WIDTH(80),
      .LSB(0)
  ) key_lfsr (
      .clk(clk),
      .rst(key_lfsr_rst),
      .shift(key_lfsr_shift),
      .feedback_coeff((1 << (80 - 80)) + (1 << (80 - 61)) + (1 << (80 - 50)) + (1 << (80 - 13))),
      .initial_state(key),
      .state(key_lfsr_state)
  );

  logic counter_lfsr_shift;
  logic counter_lfsr_rst;
  logic [7:0] counter_lfsr_state;
  LFSR #(
      .DATA_WIDTH(8),
      .LSB(1)
  ) counter_lfsr (
      .clk(clk),
      .rst(counter_lfsr_rst),
      .shift(counter_lfsr_shift),
      .feedback_coeff(9'h1A9),
      .initial_state(8'hFF),
      .state(counter_lfsr_state)
  );

  encrypt #(
      .N(N)
  ) encrypt_impl (
      .clk(clk),
      .rst(rst),
      .start(rq_data),
      .blk_i(block_i),
      .x1(x1),
      .x2(x2),
      .x3(x3),
      .x4(x4),
      .x5(x5),
      .y1(y1),
      .y2(y2),
      .y3(y3),
      .y4(y4),
      .y5(y5),
      .y6(y6),
      .lfsr_counter_state(counter_lfsr_state),
      .lfsr_counter_step(counter_lfsr_shift),
      .lfsr_counter_rst(counter_lfsr_rst),
      .lfsr_key_state(key_lfsr_state),
      .lfsr_key_step(key_lfsr_shift),
      .lfsr_key_rst(key_lfsr_rst),
      .result(block_o),
      .end_encrypt(end_signal)
  );

endmodule
