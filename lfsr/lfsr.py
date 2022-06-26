# Linear-feedback shift register

def bit4():
    state = 0b1001
    for i in range(20):
        # print(f"{i} = {state:04b}")
        print(f"{state & 1}", end="")
        new_state = state >> 1
        bit = (state ^ new_state) & 1
        state = new_state  | (bit << 3)


def bit128():
    state = (1 << 127) | 1
    while True:
        # print(f"{i} = {state:04b}")
        print(f"{state & 1}", end="")
        bit = (state ^ (state >> 1) ^ (state >> 2) ^ (state >> 7)) & 1
        state = (state >> 1)  | (bit << 127)


bit128()
