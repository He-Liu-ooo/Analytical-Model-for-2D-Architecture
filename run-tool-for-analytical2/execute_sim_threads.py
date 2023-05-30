#!/usr/bin/python3
import os
import sys
from multiprocessing import Pool

run_cpt = "/home/hel/workspace/grad_proj/template-latency-sim/run-tool-for-analytical2/run_template_sim.sh"
proc_num = 10

def sim_mission(cmd):
    print(f"simulation_mission:{cmd}")
    os.system(cmd)

def exe_sim(iterate_file, mode):
    pool = Pool(proc_num)
    with open(iterate_file, "r") as f:
        ss = f.readlines()
        for s in ss:
            s = int(s.strip("\n"))
            cmd = f"{run_cpt} {s} {mode}"
            
            pool.apply_async(sim_mission, args=(cmd,))

        pool.close()
        pool.join()

if __name__ == "__main__":
    if sys.argv[1] == "-h" or len(sys.argv) != 3:
       print("usage: python3 execute_sim_threads.py iterate_file mode")       
    else:
        iterate_file = os.path.abspath(sys.argv[1])   
        os.system(f"clear")                 
        exe_sim(iterate_file, sys.argv[2])