#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : katan_values_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 16.07.2025
# Last Modified Date: 16.07.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

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
    N = int(dut.N.value)
    expected_values = katan.KATAN_VALUES[N]

    print(N)

    await Timer(10, units="ns")

    assert (
        dut.L1.value == expected_values["L1"]
    ), f'ERROR with L1, with N = {N}, expected_value = {expected_values["L1"]} and calculated = {dut.L1.value}'
    assert (
        dut.L2.value == expected_values["L2"]
    ), f'ERROR with L2, with N = {N}, expected_value = {expected_values["L2"]} and calculated = {dut.L2.value}'
    assert (
        dut.x1.value == expected_values["x1"]
    ), f'ERROR with x1, with N = {N}, expected_value = {expected_values["x1"]} and calculated = {dut.x1.value}'
    assert (
        dut.x2.value == expected_values["x2"]
    ), f'ERROR with x2, with N = {N}, expected_value = {expected_values["x2"]} and calculated = {dut.x2.value}'
    assert (
        dut.x3.value == expected_values["x3"]
    ), f'ERROR with x3, with N = {N}, expected_value = {expected_values["x3"]} and calculated = {dut.x3.value}'
    assert (
        dut.x4.value == expected_values["x4"]
    ), f'ERROR with x4, with N = {N}, expected_value = {expected_values["x4"]} and calculated = {dut.x4.value}'
    assert (
        dut.x5.value == expected_values["x5"]
    ), f'ERROR with x5, with N = {N}, expected_value = {expected_values["x5"]} and calculated = {dut.x5.value}'
    assert (
        dut.y1.value == expected_values["y1"]
    ), f'ERROR with y1, with N = {N}, expected_value = {expected_values["y1"]} and calculated = {dut.y1.value}'
    assert (
        dut.y2.value == expected_values["y2"]
    ), f'ERROR with y2, with N = {N}, expected_value = {expected_values["y2"]} and calculated = {dut.y2.value}'
    assert (
        dut.y3.value == expected_values["y3"]
    ), f'ERROR with y3, with N = {N}, expected_value = {expected_values["y3"]} and calculated = {dut.y3.value}'
    assert (
        dut.y4.value == expected_values["y4"]
    ), f'ERROR with y4, with N = {N}, expected_value = {expected_values["y4"]} and calculated = {dut.y4.value}'
    assert (
        dut.y5.value == expected_values["y5"]
    ), f'ERROR with y5, with N = {N}, expected_value = {expected_values["y5"]} and calculated = {dut.y5.value}'
    assert (
        dut.y6.value == expected_values["y6"]
    ), f'ERROR with y6, with N = {N}, expected_value = {expected_values["y6"]} and calculated = {dut.y6.value}'
