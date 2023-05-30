#!/bin/bash

# **************************** argv check ************************
ARGC=$#
if [[ "$ARGC" < 1 ]]
then
    echo "./run_template_sim.sh seq-length(32,64,384,...)"
    exit
fi

mode=$2
if [[ "$mode" == 1 ]]
then 
# ************************* params collect ***********************
core_num=$1
output_dir="/home/hel/workspace/grad_proj/template-latency-sim/run-tool-for-analytical2/"
log_name="results-mag-4-seqlen-1024.txt"
# log_suffix=".txt"
output_log=$output_dir/$log_name


# ************************* run simulation ***********************
echo "start simulating, write log into $output_log"

echo "start time of $output_log : "$(date "+%y-%m-%d %H:%M:%S")
python /home/hel/workspace/grad_proj/template-latency-sim/analytical2/main_gpt.py \
    --core-num $core_num \
    --seq-length 1024 \
    --embedding-dim 4096 \
    --traverse-mode 1 \
    --magnification 4 \
    --head-num 32 >> $output_log
elif [[ "$mode" == 2 ]]
then
# ************************* params collect ***********************
seq_len=$1
output_dir="/home/hel/workspace/grad_proj/template-latency-sim/run-tool-for-analytical2/"
log_name="results-mag-4-corenum-400.txt"
# log_suffix=".txt"
output_log=$output_dir/$log_name


# ************************* run simulation ***********************
echo "start simulating, write log into $output_log"

echo "start time of $output_log : "$(date "+%y-%m-%d %H:%M:%S")
python /home/hel/workspace/grad_proj/template-latency-sim/analytical2/main_gpt.py \
    --core-num 400 \
    --seq-length $seq_len \
    --embedding-dim 4096 \
    --traverse-mode 2 \
    --magnification 4 \
    --head-num 32 >> $output_log
else
# ************************* params collect ***********************
magnification=$1
output_dir="/home/hel/workspace/grad_proj/template-latency-sim/run-tool-for-analytical2/"
log_name="results-corenum-4-seqlen-1024.txt"
# log_suffix=".txt"
output_log=$output_dir/$log_name


# ************************* run simulation ***********************
echo "start simulating, write log into $output_log"

echo "start time of $output_log : "$(date "+%y-%m-%d %H:%M:%S")
python /home/hel/workspace/grad_proj/template-latency-sim/analytical2/main_gpt.py \
    --core-num 4 \
    --seq-length 1024 \
    --embedding-dim 4096 \
    --traverse-mode 3 \
    --magnification $magnification \
    --head-num 32 >> $output_log
fi


echo "end time of $output_log : "$(date "+%y-%m-%d %H:%M:%S")