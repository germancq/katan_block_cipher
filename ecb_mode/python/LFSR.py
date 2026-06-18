# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    LFSR.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: germancq <germancq@dte.us.es>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/12/05 16:16:32 by germancq          #+#    #+#              #
#    Updated: 2019/12/10 17:07:09 by germancq         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

"""
Linear Feedback Shift Register
    size: n bits

"""


class LFSR:

    def __init__(self, n, initial_state, feedback_coefficient, load_by_lsb=1):
        # print()
        self.n = n
        self.state = initial_state
        self.fc = feedback_coefficient
        self.load_by_lsb = load_by_lsb

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def step(self):
        bits_selected = 0
        if self.load_by_lsb == 1:
            bits_selected = self.state & (self.fc >> 1)
        else:
            bits_selected = self.state & (self.fc)
        output_bit = 0
        for i in range(0, self.n):
            output_bit = output_bit ^ ((bits_selected >> i) & 0x1)

        if self.load_by_lsb == 1:
            self.state = self.state << 1
            self.state = (output_bit & 0x1) | (self.state & ((2**self.n) - 2))
        else:
            self.state = self.state >> 1
            self.state = ((output_bit & 0x1) << ((self.n) - 1)) | (self.state)
