#!/usr/bin/python3
import sys
import math

def gen_core_num(max_pow):
    with open("seq_len.txt", "w") as f:
        # for i in range(1, int(max_pow) + 1, 40):
        #     f.write(str(i) + "\n")
        for i in range(int(max_pow) + 1):
            f.write(str(2 ** int(i)) + "\n")

if __name__ == "__main__":
    if sys.argv[1] == "-h" or len(sys.argv) != 2:
       print("usage: python3 gen_seq_len.py max_pow")       
    else:
        gen_core_num(sys.argv[1])