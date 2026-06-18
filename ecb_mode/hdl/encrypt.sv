/**
 * File              : encrypt.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 24.09.2025
 * Last Modified Date: 24.09.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */


module encrypt #(
    parameter N = 32
) (
    input clk,
    input rst,
    input start,
    input [N-1:0] blk_i,
    input [5:0] x1,
    input [5:0] x2,
    input [5:0] x3,
    input [5:0] x4,
    input [5:0] x5,
    input [5:0] y1,
    input [5:0] y2,
    input [5:0] y3,
    input [5:0] y4,
    input [5:0] y5,
    input [5:0] y6,
    input [7:0] lfsr_counter_state,
    output logic lfsr_counter_step,
    output logic lfsr_counter_rst,
    input [79:0] lfsr_key_state,
    output logic lfsr_key_step,
    output logic lfsr_key_rst,
    output [N-1:0] result,
    output logic end_encrypt
);

  assign result = {L1_reg_dout, L2_reg_dout};

  localparam L1_LEN = N == 32 ? 13 : (N == 48 ? 19 : 25);
  localparam L2_LEN = N == 32 ? 19 : (N == 48 ? 29 : 39);
  //create L1 and L2 registers
  logic L1_reg_cl;
  logic L1_reg_w;
  logic [L1_LEN-1:0] L1_reg_din;
  logic [L1_LEN-1:0] L1_reg_dout;

  register #(
      .DATA_WIDTH(L1_LEN)
  ) L1_reg (
      .clk(clk),
      .cl(L1_reg_cl),
      .w(L1_reg_w),
      .din(L1_reg_din),
      .dout(L1_reg_dout)
  );

  logic L2_reg_cl;
  logic L2_reg_w;
  logic [L2_LEN-1:0] L2_reg_din;
  logic [L2_LEN-1:0] L2_reg_dout;
  register #(
      .DATA_WIDTH(L2_LEN)
  ) L2_reg (
      .clk(clk),
      .cl(L2_reg_cl),
      .w(L2_reg_w),
      .din(L2_reg_din),
      .dout(L2_reg_dout)
  );

  //round function impl
  logic start_round;
  logic rst_round;
  logic end_round;
  logic [L1_LEN-1:0] L1_reg_round_f;
  logic [L2_LEN-1:0] L2_reg_round_f;
  round_function #(
      .L1_LEN(L1_LEN),
      .L2_LEN(L2_LEN)
  ) round_f_impl (
      .clk(clk),
      .rst(rst_round),
      .start(start_round),
      .key_reg_state(lfsr_key_state[1:0]),
      .L1_reg(L1_reg_dout),
      .L2_reg(L2_reg_dout),
      .ir(lfsr_counter_state[7]),
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
      .L1_reg_result(L1_reg_round_f),
      .L2_reg_result(L2_reg_round_f),
      .end_round(end_round)
  );

  //counter to check how many round_function performs
  logic counter_rf_rst;
  logic counter_rf_up;
  logic counter_rf_down;
  logic [2:0] counter_rf_dout;
  counter #(
      .DATA_WIDTH(3)
  ) counter_rf (
      .clk (clk),
      .rst (counter_rf_rst),
      .up  (counter_rf_up),
      .down(counter_rf_down),
      .din (1),
      .dout(counter_rf_dout)
  );


  logic [3:0] current_state, next_state;

  localparam IDLE = 0;
  localparam LOAD_PLAINTEXT = 1;
  localparam INCR_COUNTER = 2;
  localparam CHECK_END = 3;
  localparam START_ROUND_F = 4;
  localparam WAIT_ROUND_F = 5;
  localparam SHIFT_KEY_1 = 6;
  localparam SHIFT_KEY_2 = 7;
  localparam END_STATE = 8;
  localparam CHECK_N = 9;

  always_comb begin
    next_state = current_state;

    lfsr_key_step = 0;
    lfsr_counter_step = 0;

    lfsr_key_rst = 0;
    lfsr_counter_rst = 0;

    end_encrypt = 0;

    start_round = 0;
    rst_round = 0;

    L1_reg_cl = 0;
    L1_reg_w = 0;
    L1_reg_din = L1_reg_round_f;

    L2_reg_cl = 0;
    L2_reg_w = 0;
    L2_reg_din = L2_reg_round_f;

    counter_rf_rst = 0;
    counter_rf_up = 0;
    counter_rf_down = 0;

    case (current_state)
      IDLE: begin
        L1_reg_cl = 1;
        L2_reg_cl = 1;
        rst_round = 1;
        lfsr_counter_rst = 1;
        lfsr_key_rst = 1;
        counter_rf_rst = 1;
        if (start == 1) begin
          next_state = LOAD_PLAINTEXT;
        end
      end
      LOAD_PLAINTEXT: begin
        L1_reg_w   = 1;
        L1_reg_din = blk_i[N-1:L2_LEN];

        L2_reg_w   = 1;
        L2_reg_din = blk_i[L2_LEN-1:0];

        next_state = INCR_COUNTER;

      end
      INCR_COUNTER: begin

        lfsr_counter_step = 1;
        next_state = CHECK_END;

      end
      CHECK_END: begin

        next_state = START_ROUND_F;

        if (lfsr_counter_state == 8'hFF) begin
          next_state = END_STATE;
        end


      end
      START_ROUND_F: begin
        counter_rf_up = 1;
        start_round = 1;

        next_state = WAIT_ROUND_F;

      end
      WAIT_ROUND_F: begin
        if (end_round) begin
          L2_reg_din = L2_reg_round_f;
          L1_reg_din = L1_reg_round_f;
          L2_reg_w   = 1;
          L1_reg_w   = 1;
          next_state = CHECK_N;

        end

      end
      CHECK_N: begin
        if (counter_rf_dout == N[6:4]) begin
          rst_round  = 1;
          next_state = SHIFT_KEY_1;
        end else begin
          rst_round  = 1;
          next_state = START_ROUND_F;
        end

      end
      SHIFT_KEY_1: begin
        counter_rf_rst = 1;
        lfsr_key_step = 1;
        next_state = SHIFT_KEY_2;

      end
      SHIFT_KEY_2: begin
        lfsr_key_step = 1;
        next_state = INCR_COUNTER;

      end
      END_STATE: begin
        end_encrypt = 1;

      end

    endcase

  end

  always_ff @(posedge clk) begin
    if (rst == 1) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end

  end

endmodule
