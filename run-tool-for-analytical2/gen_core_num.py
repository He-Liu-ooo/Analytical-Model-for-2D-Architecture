#!/usr/bin/python3
import sys

def gen_core_num(core_num):
    with open("core_num.txt", "w") as f:
        for i in range(1, int(core_num) + 1):
            f.write(str(i ** 2) + "\n")

if __name__ == "__main__":
    if sys.argv[1] == "-h" or len(sys.argv) != 2:
       print("usage: python3 gen_core_num.py max_core_num")       
    else:
        gen_core_num(sys.argv[1])