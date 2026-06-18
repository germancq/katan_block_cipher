/**
 * File              : katan_values.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 16.07.2025
 * Last Modified Date: 16.07.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module katan_values #(
    parameter N = 32
) (
    output [5:0] L1,
    output [5:0] L2,
    output [5:0] x1,
    output [5:0] x2,
    output [5:0] x3,
    output [5:0] x4,
    output [5:0] x5,
    output [5:0] y1,
    output [5:0] y2,
    output [5:0] y3,
    output [5:0] y4,
    output [5:0] y5,
    output [5:0] y6
);

  assign L1 = N == 32 ? 13 : (N == 48 ? 19 : 25);
  assign L2 = N == 32 ? 19 : (N == 48 ? 29 : 39);
  assign x1 = N == 32 ? 12 : (N == 48 ? 18 : 24);
  assign x2 = N == 32 ? 7 : (N == 48 ? 12 : 15);
  assign x3 = N == 32 ? 8 : (N == 48 ? 15 : 20);
  assign x4 = N == 32 ? 5 : (N == 48 ? 7 : 11);
  assign x5 = N == 32 ? 3 : (N == 48 ? 6 : 9);
  assign y1 = N == 32 ? 18 : (N == 48 ? 28 : 38);
  assign y2 = N == 32 ? 7 : (N == 48 ? 19 : 25);
  assign y3 = N == 32 ? 12 : (N == 48 ? 21 : 33);
  assign y4 = N == 32 ? 10 : (N == 48 ? 13 : 21);
  assign y5 = N == 32 ? 8 : (N == 48 ? 15 : 14);
  assign y6 = N == 32 ? 3 : (N == 48 ? 6 : 9);

endmodule
