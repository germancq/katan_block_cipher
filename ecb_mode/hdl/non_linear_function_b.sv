/**
 * File              : non_linear_function_b.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 15.09.2025
 * Last Modified Date: 15.09.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module non_linear_function_b #(
    parameter L2_LEN = 19
) (
    input [$clog2(L2_LEN)-1:0] y1,
    input [$clog2(L2_LEN)-1:0] y2,
    input [$clog2(L2_LEN)-1:0] y3,
    input [$clog2(L2_LEN)-1:0] y4,
    input [$clog2(L2_LEN)-1:0] y5,
    input [$clog2(L2_LEN)-1:0] y6,
    input [L2_LEN-1:0] L2_reg,
    input rk,
    output result
);

  assign result = L2_reg[y1] ^ L2_reg[y2] ^ (L2_reg[y3] & L2_reg[y4]) ^ (L2_reg[y5] & L2_reg[y6]) ^ rk;


endmodule
