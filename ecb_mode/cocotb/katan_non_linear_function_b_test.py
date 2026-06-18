#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : katan_non_linear_function_a.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 08.09.2025
# Last Modified Date: 08.09.2025

import os
import random
import sys

import cocotb
import katan
import numpy as np
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
async def test(dut, index=0):

    N = 32

    if dut.L2_LEN.value == 19:
        N = 32
    elif dut.L2_LEN.value == 29:
        N = 48
    else:
        N = 64

    katan_values = katan.KATAN_VALUES[N]
    katan_cipher_sw = katan.KATAN(N, random.getrandbits(80))
    rk = random.getrandbits(1)

    print(N)
    print(katan_values)

    katan_values["L2"] = random.getrandbits(dut.L2_LEN.value)

    print(katan_values)

    katan_cipher_sw.L2_reg = katan_values["L2"]

    dut.y1.value = katan_values["y1"]
    dut.y2.value = katan_values["y2"]
    dut.y3.value = katan_values["y3"]
    dut.y4.value = katan_values["y4"]
    dut.y5.value = katan_values["y5"]
    dut.y6.value = katan_values["y6"]
    dut.L2_reg.value = katan_values["L2"]
    dut.rk.value = rk

    await Timer(10, units="ns")

    expected_result = katan_cipher_sw.non_linear_function_b(rk)

    print("cocotb values")
    print(hex(dut.L2_reg.value))
    print(hex(dut.y1.value))
    print(hex(dut.y2.value))
    print(hex(dut.y3.value))
    print(hex(dut.y4.value))
    print(hex(dut.y5.value))
    print(hex(dut.y6.value))
    print(dut.rk.value)

    assert (
        dut.result.value == expected_result
    ), f"ERROR with result, with N = {N}, expected_value = {expected_result} and calculated = {dut.result.value}"


n = 0x15
factory = TestFactory(test)

factory.add_option("index", range(0, n))
factory.generate_tests()
