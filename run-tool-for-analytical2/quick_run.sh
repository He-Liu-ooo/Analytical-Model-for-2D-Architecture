#!/bin/bash
# clear
rm results-mag-4-seqlen-1024.txt
python3 gen_core_num.py 40
# python3 gen_seq_len.py 16
# python3 gen_magnification.py 2 10 2
# python3 execute_sim_threads.py core_num.txt
# mode 1 for traverse core num
# mode 2 for traverse seq len
# mode 3 for traverse magnification
python3 execute_sim_threads.py core_num.txt 1