#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : katan.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 02.07.2025
# Last Modified Date: 02.07.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import LFSR

KATAN_VALUES = {
    32: {
        "L1": 13,
        "L2": 19,
        "x1": 12,
        "x2": 7,
        "x3": 8,
        "x4": 5,
        "x5": 3,
        "y1": 18,
        "y2": 7,
        "y3": 12,
        "y4": 10,
        "y5": 8,
        "y6": 3,
    },
    48: {
        "L1": 19,
        "L2": 29,
        "x1": 18,
        "x2": 12,
        "x3": 15,
        "x4": 7,
        "x5": 6,
        "y1": 28,
        "y2": 19,
        "y3": 21,
        "y4": 13,
        "y5": 15,
        "y6": 6,
    },
    64: {
        "L1": 25,
        "L2": 39,
        "x1": 24,
        "x2": 15,
        "x3": 20,
        "x4": 11,
        "x5": 9,
        "y1": 38,
        "y2": 25,
        "y3": 33,
        "y4": 21,
        "y5": 14,
        "y6": 9,
    },
}


class KATAN:

    def __init__(self, N, key):
        self.N = N
        # feedback_coeff = (1 << 80) + (1 << 61) + (1 << 50) + (1 << 13) + 1
        feedback_coeff = (
            (1 << 0) + (1 << (80 - 61)) + (1 << (80 - 50)) + (1 << (80 - 13))
        )
        self.key_reg = LFSR.LFSR(80, key, feedback_coeff, load_by_lsb=0)
        self.counter = LFSR.LFSR(8, 0xFF, 0x1A9)
        self.L1 = KATAN_VALUES[N]["L1"]
        self.L2 = KATAN_VALUES[N]["L2"]
        self.x1 = KATAN_VALUES[N]["x1"]
        self.x2 = KATAN_VALUES[N]["x2"]
        self.x3 = KATAN_VALUES[N]["x3"]
        self.x4 = KATAN_VALUES[N]["x4"]
        self.x5 = KATAN_VALUES[N]["x5"]
        self.y1 = KATAN_VALUES[N]["y1"]
        self.y2 = KATAN_VALUES[N]["y2"]
        self.y3 = KATAN_VALUES[N]["y3"]
        self.y4 = KATAN_VALUES[N]["y4"]
        self.y5 = KATAN_VALUES[N]["y5"]
        self.y6 = KATAN_VALUES[N]["y6"]
        self.L1_reg = 0
        self.L2_reg = 0

    def encrypt(self, plaintext):
        # load L1_reg and L2_reg
        L2_val = plaintext & ((2**self.L2) - 1)
        self.L2_reg = L2_val
        L1_val = (plaintext >> (self.L2)) & ((2**self.L1) - 1)
        self.L1_reg = L1_val

        i = 0

        while True:
            print("round {}".format(i))
            self.counter.step()
            print("counter is {}".format(hex(self.counter.get_state())))
            if self.counter.get_state() == 0xFF:
                break
            self.round_function()
            if self.N >= 48:
                self.round_function()
            if self.N == 64:
                self.round_function()

            self.key_reg.step()
            self.key_reg.step()
            i = i + 1

        return ((self.L1_reg) << (self.L2)) + self.L2_reg

    def round_function(self):
        key_reg_val = self.key_reg.get_state()
        print("key reg = {}".format(hex(key_reg_val)))
        rka = key_reg_val & 1
        rkb = (key_reg_val >> 1) & 1
        print("L1_reg_init = {}".format(hex(self.L1_reg)))
        print("L2_reg_init = {}".format(hex(self.L2_reg)))
        fa = self.non_linear_function_a(rka)
        fb = self.non_linear_function_b(rkb)
        self.L1_reg = ((self.L1_reg << 1) + fb) & ((2**self.L1) - 1)
        print("L1_after_round is {}".format(hex(self.L1_reg)))
        self.L2_reg = ((self.L2_reg << 1) + fa) & ((2**self.L2) - 1)
        print("L2 after round is {}".format(hex(self.L2_reg)))

    def non_linear_function_a(self, rk):
        L1_x1 = (self.L1_reg >> (self.x1)) & 1
        L1_x2 = (self.L1_reg >> (self.x2)) & 1
        L1_x3 = (self.L1_reg >> (self.x3)) & 1
        L1_x4 = (self.L1_reg >> (self.x4)) & 1
        L1_x5 = (self.L1_reg >> (self.x5)) & 1
        print("self L1 reg = {}".format(hex(self.L1_reg)))
        print(
            "x1 = {}, x2 = {}, x3 = {}, x4 = {}, x5 = {}".format(
                L1_x1, L1_x2, L1_x3, L1_x4, L1_x5
            )
        )
        # MSB of counter
        IR = (self.counter.get_state() >> 7) & 1
        print("IR is {}".format(IR))
        result = L1_x1 ^ L1_x2 ^ (L1_x3 & L1_x4) ^ (IR & L1_x5) ^ rk
        print("fa is {}".format(result))
        return result

    def non_linear_function_b(self, rk):
        L2_y1 = (self.L2_reg >> (self.y1)) & 1
        L2_y2 = (self.L2_reg >> (self.y2)) & 1
        L2_y3 = (self.L2_reg >> (self.y3)) & 1
        L2_y4 = (self.L2_reg >> (self.y4)) & 1
        L2_y5 = (self.L2_reg >> (self.y5)) & 1
        L2_y6 = (self.L2_reg >> (self.y6)) & 1
        result = L2_y1 ^ L2_y2 ^ (L2_y3 & L2_y4) ^ (L2_y5 & L2_y6) ^ rk
        return result


if __name__ == "__main__":
    print("KATAN")
    key = 0x102030405060708090A0
    plaintext = 0x12345678
    katan = KATAN(64, key)
    result = katan.encrypt(plaintext)
    print(hex(result))
