/**
 * File              : non_linear_function_a.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 08.09.2025
 * Last Modified Date: 08.09.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */
//IR = counter_state[7]
module non_linear_function_a #(
    parameter L1_LEN = 13
) (
    input [($clog2(L1_LEN)-1):0] x1,
    input [($clog2(L1_LEN)-1):0] x2,
    input [($clog2(L1_LEN)-1):0] x3,
    input [($clog2(L1_LEN)-1):0] x4,
    input [($clog2(L1_LEN)-1):0] x5,
    input rk,
    input ir,
    input [L1_LEN-1:0] L1_reg,
    output result
);

  assign result = L1_reg[x1] ^ L1_reg[x2] ^ (L1_reg[x3] & L1_reg[x4]) ^ (ir & L1_reg[x5]) ^ rk;

endmodule
