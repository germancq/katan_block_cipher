/**
 * File              : round_function.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 16.09.2025
 * Last Modified Date: 16.09.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module round_function #(
    parameter L1_LEN = 13,
    parameter L2_LEN = 19
) (
    input clk,
    input rst,
    input start,
    input [1:0] key_reg_state,
    input [L1_LEN-1:0] L1_reg,
    input [L2_LEN-1:0] L2_reg,
    input ir,
    input [($clog2(L1_LEN)-1):0] x1,
    input [($clog2(L1_LEN)-1):0] x2,
    input [($clog2(L1_LEN)-1):0] x3,
    input [($clog2(L1_LEN)-1):0] x4,
    input [($clog2(L1_LEN)-1):0] x5,
    input [$clog2(L2_LEN)-1:0] y1,
    input [$clog2(L2_LEN)-1:0] y2,
    input [$clog2(L2_LEN)-1:0] y3,
    input [$clog2(L2_LEN)-1:0] y4,
    input [$clog2(L2_LEN)-1:0] y5,
    input [$clog2(L2_LEN)-1:0] y6,
    output [L1_LEN-1:0] L1_reg_result,
    output [L2_LEN-1:0] L2_reg_result,
    output logic end_round

);

  assign L1_reg_result = {L1_reg[L1_LEN-2:0], f_reg_dout[1]};
  assign L2_reg_result = {L2_reg[L2_LEN-2:0], f_reg_dout[0]};

  logic [0:0] f_reg_cl[1:0];
  logic [0:0] f_reg_w[1:0];
  logic [0:0] f_reg_din[1:0];
  logic [0:0] f_reg_dout[1:0];
  genvar i;
  generate
    for (i = 0; i < 2; i++) begin
      register #(
          .DATA_WIDTH(1)
      ) f_reg (
          .clk(clk),
          .cl(f_reg_cl[i]),
          .w(f_reg_w[i]),
          .din(f_reg_din[i]),
          .dout(f_reg_dout[i])
      );

    end
  endgenerate


  non_linear_function_a #(
      .L1_LEN(L1_LEN)
  ) fa (
      .x1(x1),
      .x2(x2),
      .x3(x3),
      .x4(x4),
      .x5(x5),
      .rk(key_reg_state[0]),
      .ir(ir),
      .L1_reg(L1_reg),
      .result(f_reg_din[0])
  );

  non_linear_function_b #(
      .L2_LEN(L2_LEN)
  ) fb (
      .y1(y1),
      .y2(y2),
      .y3(y3),
      .y4(y4),
      .y5(y5),
      .y6(y6),
      .L2_reg(L2_reg),
      .rk(key_reg_state[1]),
      .result(f_reg_din[1])
  );


  logic [1:0] current_state, next_state;

  localparam IDLE = 0;
  localparam CALCULATE_F = 1;
  localparam END_STATE = 2;

  logic [31:0] j;

  always_comb begin
    next_state = current_state;
    end_round  = 0;

    for (j = 0; j < 2; j++) begin
      f_reg_cl[j] = 0;
      f_reg_w[j]  = 0;
    end

    case (current_state)
      IDLE: begin

        for (j = 0; j < 2; j++) begin
          f_reg_cl[j] = 1;
        end

        if (start) begin
          next_state = CALCULATE_F;
        end

      end

      CALCULATE_F: begin
        for (j = 0; j < 2; j++) begin
          f_reg_w[j] = 1;
        end
        next_state = END_STATE;

      end

      END_STATE: begin
        end_round = 1;
      end

    endcase
  end

  always_ff @(posedge clk) begin
    if (rst) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end
  end
endmodule
