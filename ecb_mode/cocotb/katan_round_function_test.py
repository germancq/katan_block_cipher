#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : katan_round_function_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 16.09.2025
# Last Modified Date: 16.09.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import os
import random
import sys

import cocotb
import katan
import numpy as np
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


def setup_dut(dut, key_reg_state, ir, katan_values, L1_reg, L2_reg):
    cocotb.fork(Clock(dut.clk, CLK_PERIOD).start())
    dut.rst.value = 0
    dut.start.value = 0
    dut.key_reg_state.value = key_reg_state
    dut.L1_reg.value = L1_reg
    dut.L2_reg.value = L2_reg
    dut.ir.value = ir
    dut.x1.value = katan_values["x1"]
    dut.x2.value = katan_values["x2"]
    dut.x3.value = katan_values["x3"]
    dut.x4.value = katan_values["x4"]
    dut.x5.value = katan_values["x5"]
    dut.y1.value = katan_values["y1"]
    dut.y2.value = katan_values["y2"]
    dut.y3.value = katan_values["y3"]
    dut.y4.value = katan_values["y4"]
    dut.y5.value = katan_values["y5"]
    dut.y6.value = katan_values["y6"]


async def rst_function_test(dut):
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"
    await n_cycles_clock(dut, 10)
    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"
    for i in range(0, 2):
        assert dut.f_reg_cl[i].value == 1, f"ERROR clear signals {i}"
        assert dut.f_reg_dout[i].value == 0, f"ERROR output reg signals {i}"

    assert dut.end_round.value == 0, f"ERROR in end_round signal"


async def calculate_f_function_test(dut, fa, fb):
    dut.rst.value = 0
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.current_state.value}"
    dut.start.value = 1
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.CALCULATE_F.value
    ), f"ERROR STATE IN CALCULATE_F, STATE={dut.current_state.value}"

    assert dut.f_reg_din[0].value == fa, f"ERROR in CALCULATE_F fa value must be {fa}"
    assert dut.f_reg_din[1].value == fb, f"ERROR in CALCULATE_F fb value must be {fb}"
    assert dut.end_round.value == 0, f"ERROR in end_round signal"


async def end_state_function_test(dut, katan_cipher_sw):
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.END_STATE.value
    ), f"ERROR STATE IN END, STATE={dut.current_state.value}"
    assert dut.end_round.value == 1, f"ERROR in end_round signal"
    assert (
        dut.L1_reg_result.value == katan_cipher_sw.L1_reg
    ), f"ERROR in L1 result calculated = {hex(dut.L1_reg_result.value)}, expected={hex(katan_cipher_sw.L1_reg)}"

    assert (
        dut.L2_reg_result.value == katan_cipher_sw.L2_reg
    ), f"ERROR in L2 result calculated = {hex(dut.L2_reg_result.value)}, expected={hex(katan_cipher_sw.L2_reg)}"


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
    key = random.getrandbits(80)
    katan_cipher_sw = katan.KATAN(N, key)
    katan_cipher_sw.L1_reg = random.getrandbits(dut.L1_LEN.value)
    katan_cipher_sw.L2_reg = random.getrandbits(dut.L2_LEN.value)

    for i in (0, random.randint(10, 50)):
        katan_cipher_sw.counter.step()

    counter_state = katan_cipher_sw.counter.get_state()
    key_state = katan_cipher_sw.key_reg.get_state()

    ir = (counter_state >> 7) & 1
    key_reg_state = (key_state) & 0x3
    rka = key_state & 1
    rkb = (key_state >> 1) & 1
    fa = katan_cipher_sw.non_linear_function_a(rka)
    fb = katan_cipher_sw.non_linear_function_b(rkb)

    setup_dut(
        dut,
        key_reg_state,
        ir,
        katan_values,
        katan_cipher_sw.L1_reg,
        katan_cipher_sw.L2_reg,
    )

    katan_cipher_sw.round_function()

    await rst_function_test(dut)
    await calculate_f_function_test(dut, fa, fb)
    await end_state_function_test(dut, katan_cipher_sw)


n = 0x15
factory = TestFactory(test)

factory.add_option("index", range(0, n))
factory.generate_tests()
