#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : katan_encrypt_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 30.09.2025
# Last Modified Date: 30.09.2025
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


def setup_dut(dut, key, plaintext):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.key.value = key
    dut.block_i.value = plaintext
    dut.enc_dec.value = 0
    dut.rq_data.value = 0


async def rst_function_test(dut):
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.encrypt_impl.current_state.value}"
    await n_cycles_clock(dut, 10)
    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.encrypt_impl.current_state.value}"

    assert dut.encrypt_impl.L1_reg_cl.value == 1, f"ERROR in L1_reg_cl signal"
    assert dut.encrypt_impl.L2_reg_cl.value == 1, f"ERROR in L2_reg_cl signal"
    assert dut.encrypt_impl.rst_round.value == 1, f"ERROR in rst_round signal"
    assert (
        dut.encrypt_impl.lfsr_counter_rst.value == 1
    ), f"ERROR in lfsr_counter_rst signal"
    assert dut.encrypt_impl.lfsr_key_rst.value == 1, f"ERROR in lfsr_key_rst signal"
    assert dut.encrypt_impl.counter_rf_rst.value == 1, f"ERROR in counter_rf_rst signal"

    assert (
        dut.encrypt_impl.lfsr_key_state.value == dut.key.value
    ), f"ERROR initial key state"
    assert (
        dut.encrypt_impl.lfsr_counter_state.value == 0xFF
    ), f"ERROR initial counter state"
    assert int(dut.encrypt_impl.round_f_impl.current_state.value) == int(
        dut.encrypt_impl.round_f_impl.IDLE
    ), f"ERROR state in round_f"


async def load_plaintext_test(dut, katan_sw):
    dut.rst.value = 0
    await n_cycles_clock(dut, 1)
    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.IDLE.value
    ), f"ERROR STATE IN RST, STATE={dut.encrypt_impl.current_state.value}"

    dut.rq_data.value = 1
    await n_cycles_clock(dut, 1)

    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.LOAD_PLAINTEXT.value
    ), f"ERROR STATE IN LOAD_PLAINTEXT, STATE={dut.encrypt_impl.current_state.value}"

    print("L1_input is {}".format(hex(dut.encrypt_impl.L1_reg_din.value)))
    print("L2_input is {}".format(hex(dut.encrypt_impl.L2_reg_din.value)))
    print("L1_input is {}".format(hex(dut.encrypt_impl.L1_reg.din.value)))
    print("L2_input is {}".format(hex(dut.encrypt_impl.L2_reg.din.value)))
    print("plaintext is {}".format(hex(dut.block_i.value)))

    assert dut.encrypt_impl.L1_reg_w.value == 1, f"ERROR L1_w"
    assert dut.encrypt_impl.L2_reg_w.value == 1, f"ERROR L2_w"
    assert dut.encrypt_impl.L1_reg_cl.value == 0, f"ERROR L1_cl"
    assert dut.encrypt_impl.L2_reg_cl.value == 0, f"ERROR L2_cl"

    assert dut.encrypt_impl.L1_reg.w.value == 1, f"ERROR L1_w"
    assert dut.encrypt_impl.L2_reg.w.value == 1, f"ERROR L2_w"
    assert dut.encrypt_impl.L1_reg.cl.value == 0, f"ERROR L1_cl"
    assert dut.encrypt_impl.L2_reg.cl.value == 0, f"ERROR L2_cl"

    await n_cycles_clock(dut, 1)

    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.INCR_COUNTER.value
    ), f"ERROR STATE IN INCR_COUNTER, STATE={dut.encrypt_impl.current_state.value}"

    # load L1_reg and L2_reg
    L2_val = dut.block_i.value & ((2**katan_sw.L2) - 1)
    katan_sw.L2_reg = L2_val
    L1_val = (dut.block_i.value >> (katan_sw.L2)) & ((2**katan_sw.L1) - 1)
    katan_sw.L1_reg = L1_val

    print("plaintext is {}".format(hex(dut.block_i.value)))
    print("L1_output is {}".format(hex(dut.encrypt_impl.L1_reg.dout.value)))
    print("L2_output is {}".format(hex(dut.encrypt_impl.L2_reg.dout.value)))
    assert dut.encrypt_impl.L1_reg_w.value == 0, f"ERROR L1_w"
    assert dut.encrypt_impl.L2_reg_w.value == 0, f"ERROR L2_w"
    assert dut.encrypt_impl.L1_reg_cl.value == 0, f"ERROR L1_cl"
    assert dut.encrypt_impl.L2_reg_cl.value == 0, f"ERROR L2_cl"

    assert dut.encrypt_impl.L1_reg.w.value == 0, f"ERROR L1_w"
    assert dut.encrypt_impl.L2_reg.w.value == 0, f"ERROR L2_w"
    assert dut.encrypt_impl.L1_reg.cl.value == 0, f"ERROR L1_cl"
    assert dut.encrypt_impl.L2_reg.cl.value == 0, f"ERROR L2_cl"

    assert (
        dut.encrypt_impl.L2_reg_dout.value == katan_sw.L2_reg
    ), f"ERROR loading plaintext, expected={hex(katan_sw.L2_reg)}, calculated={hex(dut.encrypt_impl.L2_reg_dout.value)}"

    assert (
        dut.encrypt_impl.L1_reg_dout.value == katan_sw.L1_reg
    ), f"ERROR loading plaintext, expected={hex(katan_sw.L1_reg)}, calculated={hex(dut.encrypt_impl.L1_reg_dout.value)}"


async def encrypt_loop_test(dut, katan_sw):

    i = 0
    while True:

        print("ciclo {}".format(i))

        i = i + 1

        assert int(dut.encrypt_impl.current_state.value) == int(
            dut.encrypt_impl.INCR_COUNTER.value
        ), f"ERROR STATE IN INCR_COUNTER, STATE={dut.encrypt_impl.current_state.value}"

        await n_cycles_clock(dut, 1)

        assert int(dut.encrypt_impl.current_state.value) == int(
            dut.encrypt_impl.CHECK_END.value
        ), f"ERROR STATE IN CHECK_END, STATE={dut.encrypt_impl.current_state.value}"

        katan_sw.counter.step()

        assert (
            dut.encrypt_impl.lfsr_counter_state.value == katan_sw.counter.get_state()
        ), f"ERROR in counter state, expected={hex(katan_sw.counter.get_state())}, calculated = {hex(dut.encrypt_impl.lfsr_counter_state.value)}"

        if dut.encrypt_impl.lfsr_counter_state.value == 0xFF:
            return

        n = 3
        if dut.N.value == 32:
            n = 1
        elif dut.N.value == 48:
            n = 2

        for j in range(0, n):
            await n_cycles_clock(dut, 1)

            assert int(dut.encrypt_impl.current_state.value) == int(
                dut.encrypt_impl.START_ROUND_F.value
            ), f"ERROR STATE IN START_ROUND_F, STATE={dut.encrypt_impl.current_state.value}"

            await n_cycles_clock(dut, 1)

            assert int(dut.encrypt_impl.current_state.value) == int(
                dut.encrypt_impl.WAIT_ROUND_F.value
            ), f"ERROR STATE IN WAIT_ROUND_F, STATE={dut.encrypt_impl.current_state.value}"

            while dut.encrypt_impl.end_round.value == 0:
                await n_cycles_clock(dut, 1)

            assert int(dut.encrypt_impl.current_state.value) == int(
                dut.encrypt_impl.WAIT_ROUND_F.value
            ), f"ERROR STATE IN WAIT_ROUND_F, STATE={dut.encrypt_impl.current_state.value}"

            await n_cycles_clock(dut, 1)

            katan_sw.round_function()

            print(
                "counter_rf_dout == {}".format(
                    hex(dut.encrypt_impl.counter_rf_dout.value)
                )
            )

            assert (
                dut.encrypt_impl.L1_reg_dout.value == katan_sw.L1_reg
            ), f"ERROR loading plaintext, expected={hex(katan_sw.L1_reg)}, calculated={hex(dut.encrypt_impl.L1_reg_dout.value)}"

            assert (
                dut.encrypt_impl.L2_reg_dout.value == katan_sw.L2_reg
            ), f"ERROR loading plaintext, expected={hex(katan_sw.L2_reg)}, calculated={hex(dut.encrypt_impl.L2_reg_dout.value)}"

            assert int(dut.encrypt_impl.current_state.value) == int(
                dut.encrypt_impl.CHECK_N.value
            ), f"ERROR STATE IN CHECK_N, STATE={dut.encrypt_impl.current_state.value}"

        await n_cycles_clock(dut, 1)
        assert int(dut.encrypt_impl.current_state.value) == int(
            dut.encrypt_impl.SHIFT_KEY_1.value
        ), f"ERROR STATE IN SHIFT_KEY_1, STATE={dut.encrypt_impl.current_state.value}"

        katan_sw.key_reg.step()

        await n_cycles_clock(dut, 1)

        assert (
            dut.encrypt_impl.lfsr_key_state.value == katan_sw.key_reg.get_state()
        ), f"ERROR in key state, expected={hex(katan_sw.key_reg.get_state())}, calculated = {hex(dut.encrypt_impl.lfsr_key_state.value)}"

        assert int(dut.encrypt_impl.current_state.value) == int(
            dut.encrypt_impl.SHIFT_KEY_2.value
        ), f"ERROR STATE IN SHIFT_KEY_1, STATE={dut.encrypt_impl.current_state.value}"

        katan_sw.key_reg.step()

        await n_cycles_clock(dut, 1)

        assert (
            dut.encrypt_impl.lfsr_key_state.value == katan_sw.key_reg.get_state()
        ), f"ERROR in key state, expected={hex(katan_sw.key_reg.get_state())}, calculated = {hex(dut.encrypt_impl.lfsr_key_state.value)}"


async def end_state_function_test(dut, katan_sw):
    await n_cycles_clock(dut, 1)
    assert int(dut.encrypt_impl.current_state.value) == int(
        dut.encrypt_impl.END_STATE.value
    ), f"ERROR STATE IN END, STATE={dut.encrypt_impl.current_state.value}"
    assert dut.end_signal.value == 1, f"ERROR in end_round signal"

    expected_result = ((katan_sw.L1_reg) << (katan_sw.L2)) + katan_sw.L2_reg

    assert (
        dut.block_o.value == expected_result
    ), f"ERROR in result, expected = {hex(expected_result)}, calculated = {dut.block_o.value}"


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):
    N = int(dut.N.value)

    random.seed(index)

    key = random.getrandbits(80)
    plaintext = random.getrandbits(N)
    katan_cipher_sw = katan.KATAN(N, key)

    setup_dut(dut, key, plaintext)

    await rst_function_test(dut)
    await load_plaintext_test(dut, katan_cipher_sw)
    await encrypt_loop_test(dut, katan_cipher_sw)
    await end_state_function_test(dut, katan_cipher_sw)
