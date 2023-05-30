#!/usr/bin/python3
import sys
import math

def gen_magnification(min, max, step):
    with open("magnification.txt", "w") as f:
        # for i in range(1, int(max_pow) + 1, 40):
        #     f.write(str(i) + "\n")
        for i in range(int(min), int(max) + 1, int(step)):
            f.write(str(i) + "\n")

if __name__ == "__main__":
    if sys.argv[1] == "-h" or len(sys.argv) != 4:
       print("usage: python3 gen_seq_len.py min max step")       
    else:
        gen_magnification(sys.argv[1], sys.argv[2], sys.argv[3])