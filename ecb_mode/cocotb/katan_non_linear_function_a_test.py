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
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    random.seed(index)

    N = 32

    if dut.L1_LEN.value == 13:
        N = 32
    elif dut.L1_LEN.value == 19:
        N = 48
    else:
        N = 64

    katan_values = katan.KATAN_VALUES[N]
    katan_cipher_sw = katan.KATAN(N, random.getrandbits(80))
    rk = random.getrandbits(1)

    print(N)
    print(katan_values)

    katan_values["L1"] = random.getrandbits(dut.L1_LEN.value)

    print(katan_values)

    katan_cipher_sw.L1_reg = katan_values["L1"]

    for i in (0, random.randint(10, 50)):
        katan_cipher_sw.counter.step()

    counter_state = katan_cipher_sw.counter.get_state()

    dut.x1.value = katan_values["x1"]
    dut.x2.value = katan_values["x2"]
    dut.x3.value = katan_values["x3"]
    dut.x4.value = katan_values["x4"]
    dut.x5.value = katan_values["x5"]
    dut.L1_reg.value = katan_values["L1"]
    dut.rk.value = rk
    dut.ir.value = (counter_state >> 7) & 1

    await Timer(10, units="ns")

    expected_result = katan_cipher_sw.non_linear_function_a(rk)

    print("cocotb values")
    print(hex(dut.L1_reg.value))
    print(hex(dut.x1.value))
    print(hex(dut.x2.value))
    print(hex(dut.x3.value))
    print(hex(dut.x4.value))
    print(hex(dut.x5.value))
    print(dut.rk.value)
    print(dut.ir.value)

    assert (
        dut.result.value == expected_result
    ), f"ERROR with result, with N = {N}, expected_value = {expected_result} and calculated = {dut.result.value}"
