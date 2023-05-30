
import argparse
import sys
import math
import utils
from mappings import Mappings

"""
Metrics: 

Latency:
Items contribute to Latency:
Computation Latency
Configuration switch Latency
Weight loading Latency(relates to bandwidth, which relates to the core number)
Results write-back Latency

Energy:
Item contributes to Energy:
Computation Energy
Configuration Energy
GB read Energy
GB write Energy
SRAM write Energy
SRAM read Energy

NOTE:
it is suggested that when we traverse core number, we only traverse those square number
"""

def argparser():
    """ Argument parser. """

    ap = argparse.ArgumentParser()

    """ HW configs """
    """ Device configs """
    ap.add_argument('--die_num', type = int, default = 16,
                    help = 'number of 10mm*10mm die, should be the square of int')
    # ap.add_argument('--core-num', type = int, default = 1, 
    #                 help = 'number of matrix computation core')
    ap.add_argument('--SRAM-capacity', type = int, default = 65536, 
                    help = 'capacity of SRAM in matrix computation core, in term of BYTE')
    ap.add_argument('--MAC-lane', type = int, default = 16, 
                    help = 'number of MAC lane in matrix computation core(how many vector dot production can calculate in parallel)')
    ap.add_argument('--MAC-num', type = int, default = 32, 
                    help = 'number of MAC within a lane(dimension of a dot production)')
    """ Latency configs """                               
    ap.add_argument('--cal-latency', type = int, default = 1,    
                    help = 'latency of calculate a mac_num * mac_num dot production, normalized to METATIME')
    ap.add_argument('--config-switch-latency', type = int, default = 50, 
                    help = 'latency of switching cofiguration of a core, normalized to METATIME')
    # ap.add_argument('--GB-SRAM-latency', type = int, default = 0.5, 
    #                 help = 'latency of moving a mac_num BYTE of data from GB into core\'s SRAM when within bandwith boundary, normalized to METATIME')
    # ap.add_argument('--vector-remove-latency', type = int, default = 4, 
    #                 help = 'latency of removing a 1 * mac_lane vector from array to GB when within bandwidth boundary, normalized to METATIME')
    ap.add_argument('--GB-bandwidth', type = int, default = 819 * 2,
                    help = 'data that can be provided by global buffer with a METATIME when core is 1, in the unit of GBps')
    """ Energy configs """
    # ap.add_argument('--cal-energy', type = int, default = 23.8,   
    #                 help = 'energy of calculating 16(mac_lane) mac_num * mac_num dot production and accumulation, normalized to METAENERGY')
    # ap.add_argument('--partial-sum-add-energy', type = int, default = 2, #TODO
    #                 help = 'energy of adding partial sum to get a complete sum of a 1 * mac_lane vector, when the partition type is \'partial sum\', normalized to cal-energy')
    # ap.add_argument('--config-switch-energy', type = int, default = 1250,  #TODO
    #                 help = 'energy of switching configuration of a core, normalized to METAENERGY')
    #...pJ/bit
    # HBM read/write energy LPDDR4 ~3pJ/bit
    #JSSCC Simba SRAM energy 16nm->5nm sqrt{}
    # ap.add_argument('--GB-read-energy', type = int, default = 800,  #TODO
    #                 help = 'energy of reading a mac_num BYTE from GB, normalized to METAENERGY, ignore NoC')
    # ap.add_argument('--GB-write-energy', type = int, default = 800,   #TODO
    #                 help = 'energy of writting a mac_lane BYTE to GB, normalized to METAENERGY, ignore NoC')
    # ap.add_argument('--SRAM-read-energy', type = int, default = 130,  #TODO
    #                 help = 'energy of reading a mac_num BYTE from core SRAM, normalized to METAENERGY')
    # ap.add_argument('--SRAM-write-energy', type = int, default = 130,  #TODO
    #                 help = 'energy of writting a mac_num BYTE from core SRAM, normalized to METAENERGY')
    # ap.add_argument('--magnification', type = int, default = 6, #TODO
    #                 help = 'how many times is GB read/write energy to calculation energy(for the same amount of data, and multiple mac_lane to get the real magnification)')

    """ SW configs """
    ap.add_argument('--seq-length', type = int, default = 1024,  
                    help = 'sequence length of the workload')
    ap.add_argument('--embedding-dim', type = int, default = 12288, 
                    help = 'embedding dimension of a token')
    ap.add_argument('--head-num', type = int, default = 96, 
                    help = 'number of attention heads')
    
    ap.add_argument('--debug-flag', type = bool, default = False)
    ap.add_argument('--traverse-mode', type = int, default = 1,
                    help = '1 for traversing core number, 2 for traversing sequence length, 3 for traversing magnification')
    
    return ap

def dump_configs(args):

    print("----------------------------------------------")
    print("| Configuration")
    print("|")
    print("| HW configs")
    print("| + clk frequency: 1.5GHz")
    print("| + die number: " + str(args.die_num))
    print("| + core SRAM capacity: " + str(args.SRAM_capacity))
    print("| + mac lane number: " + str(args.MAC_lane))
    print("| + mac number within a lane: " + str(args.MAC_num))
    # print("| + calculation latency: " + str(args.cal_latency * utils.METATIME) + "ns")
    # print("| + partial sum add latency: " + str(args.cal_latency * args.partial_sum_add_latency * utils.METATIME) + "ns")
    # print("| + configuration switching latency: " + str(args.config_switch_latency * utils.METATIME) + "ns")
    # print("| + GB -> SRAM latency: " + str(args.GB_SRAM_latency * utils.METATIME) + "ns")
    # print("| + vector removing latency: " + str(args.GB_SRAM_latency * utils.METATIME) + "ns")
    print("| + GB bandwidth: " + str(2 * args.GB_bandwidth))
    # print("| + calculation energy: " + str(args.cal_energy * utils.METAENERGY / args.MAC_lane) + "pJ")
    # print("| + partial_sum_add_energy: " + str(args.partial_sum_add_energy * utils.METAENERGY) + "pJ")
    # print("| + configuration switching energy: " + str(args.config_switch_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(args.core_num)) + "pJ")
    # print("| + GB read energy: " + str(args.magnification * args.cal_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(args.core_num)) + "pJ")
    # print("| + GB write energy: " + str(args.magnification * args.cal_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(args.core_num)) + "pJ")
    # print("| + SRAM read energy: " + str(((args.magnification * args.cal_energy) / 6) * utils.METAENERGY) + "pJ")
    # print("| + SRAM write energy: " + str(((args.magnification * args.cal_energy) / 6) * utils.METAENERGY) + "pJ")
    print("|")
    print("| SW configs")
    print("| + sequence length: " + str(args.seq_length))
    print("| + embedding dimension: " + str(args.embedding_dim))
    print("| + head number: " + str(args.head_num))
    print("----------------------------------------------")

# def dump_result(sum_latency, latencys, sum_energy, energys):

#     print("----------------------------------------------")
#     print("| Results")
#     print("|")
#     print("| Latency")
#     print("| + overall latency: " + str(sum_latency) + "ns")
#     print("| + calculation latency: " + str(latencys[0]) + "ns")
#     print("| + configuration latency: " + str(latencys[1]) + "ns")
#     print("| + weight loading latency: " + str(latencys[2]) + "ns")
#     print("| + K loading latency: " + str(latencys[3]) + "ns")
#     print("| + V loading latency: " + str(latencys[4]) + "ns")
#     print("| + write back latency: " + str(latencys[5]) + "ns")
#     print("|")
#     print("| Energy")
#     print("| + overall energy: " + str(sum_energy) + "pJ")
#     print("| + calculation energy: " + str(energys[0]) + "pJ")
#     print("| + configuration energy: " + str(energys[1]) + "pJ")
#     print("| + GB read energy for weight: " + str(energys[2]) + "pJ")
#     print("| + GB read energy for K: " + str(energys[3]) + "pJ")
#     print("| + GB read energy for V: " + str(energys[4]) + "pJ")
#     print("| + GB read energy for IA: " + str(energys[5]) + "pJ")
#     print("| + GB write energy: " + str(energys[6]) + "pJ")
#     print("| + SRAM read energy: " + str(energys[7]) + "pJ")
#     print("| + SRAM write energy: " + str(energys[8]) + "pJ")
#     print("| + other energy: " + str(energys[9]) + "pJ")
#     print("----------------------------------------------") 

#     # [cal_ltcy, config_ltcy, weight_loading_ltcy, write_back_ltcy], sum_ergy, [cal_ergy, config_ergy, gb_read_ergy, gb_write_ergy, sram_read_ergy, sram_write_ergy]

def dump_partitions(blocknum_col_qkv, blocknum_col_qk, blocknum_col_av, blocknum_col_lp, blocknum_col_fc1, blocknum_col_fc2, \
                        subsum_cnt_qkv, subsum_cnt_qk, subsum_cnt_av, subsum_cnt_lp, subsum_cnt_fc1, subsum_cnt_fc2):
    print("----------------------------------------------")
    print("| Partitions")
    print("|")
    print("| Blocknum Col")
    print("| + blocknum_col_qkv: " + str(blocknum_col_qkv))
    print("| + blocknum_col_qk: " + str(blocknum_col_qk))
    print("| + blocknum_col_av: " + str(blocknum_col_av))
    print("| + blocknum_col_lp: " + str(blocknum_col_lp))
    print("| + blocknum_col_fc1: " + str(blocknum_col_fc1))
    print("| + blocknum_col_fc2: " + str(blocknum_col_fc2))
    print("| Subsum Cnt")
    print("| + subsum_cnt_qkv: " + str(subsum_cnt_qkv))
    print("| + subsum_cnt_qk: " + str(subsum_cnt_qk))
    print("| + subsum_cnt_av: " + str(subsum_cnt_av))
    print("| + subsum_cnt_lp: " + str(subsum_cnt_lp))
    print("| + subsum_cnt_fc1: " + str(subsum_cnt_fc1))
    print("| + subsum_cnt_fc2: " + str(subsum_cnt_fc2))
    print("----------------------------------------------")
    
def analysis(subsum_cnt, blocknum_col, core_num, partial_sum_add_energy, idle_core_num, stage_idx, debug_flag):
    """ 
    subsum_cnt: subsum_cnt_qkv/subsum_cnt_qk/subsum_cnt_av/subsum_cnt_lp/subsum_cnt_fc1/subsum_cnt_fc2
    blocknum_col: blocknum_col_qkv/blocknum_col_qk/blocknum_col_av/blocknum_col_lp/blocknum_col_fc1/blocknum_col_fc2/
    """

    if debug_flag == True:
        print("****************************************")
        print("stage: " + str(stage_idx))

    global sram1_height 
    global mac_lane
    global mac_num

    global cal_latency
    global weight_loading_latency
    global write_back_latency
    global new_bandwidth

    sum_ltcy = 0
    cal_ltcy = 0
    # only static weight
    weight_loading_ltcy = 0
    K_loading_ltcy = 0
    V_loading_ltcy = 0
    write_back_ltcy = 0
    # IA laoding latency can always be hidden by weight loading latency

    cal_ergy = 0
    gb_read_ergy_weight = 0
    gb_read_ergy_K = 0
    gb_read_ergy_V = 0
    gb_read_ergy_IA = 0
    # write the result vector back into GB
    gb_write_ergy = 0
    # read SRAM for calculation
    sram_read_ergy = 0
    # write weight/IA/K/V from GB to SRAM
    sram_write_ergy = 0
    # read partial sum from prev 
    other_ergy = 0

    # subsum number a sram2 should hold
    subsum_sram1 = math.ceil((subsum_cnt * blocknum_col) / core_num)
    subsum_sram1_real = (subsum_cnt * blocknum_col) / core_num
    if subsum_sram1_real <= sram1_height:
        # if sram1 can hold all partitioned data
        if subsum_sram1_real >= subsum_cnt:
            # 2
            # if a SRAM1 can hold more than 1 mac_lane cols of data, say 2.4
            # we hold the integer part, say 2
            blocknum_col_first = subsum_sram1 // subsum_cnt
            if debug_flag == True:
                print("blocknum_col_first: " + str(blocknum_col_first))
            # 2.1
            # if adding a mac_lane col to some SRAM1 is ok
            # 2.2
            # if adding a mac_lane col to some SRAM1 exceeds the limit
            # they are the same
            core_num_act = blocknum_col - blocknum_col_first * core_num
            if debug_flag == True:
                print("core_num_act: " + str(core_num_act))

            weight_loading_latency_tmp = (core_num_act * mac_num) / (new_bandwidth * math.pow(2, 30))
            write_back_latency_tmp = weight_loading_latency_tmp
            # we need to check the bandwidth here since not all cores need to be assigned data for
            # if core_num_act > new_bdwidth:
            #     # Demanding GB bandwidth is beyond the bandwidth limit, weight loading latency and write back latency should be more than org
            #     weight_loading_latency_tmp = weight_loading_latency_org * core_num_act / new_bdwidth
            #     write_back_latency_tmp = write_back_latency_org * core_num_act / new_bdwidth
            # else:
            #     weight_loading_latency_tmp = weight_loading_latency_org
            #     write_back_latency_tmp = write_back_latency_org

            if stage_idx == 1:
                K_loading_ltcy += mac_lane * blocknum_col_first * subsum_cnt * weight_loading_latency
                K_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
            elif stage_idx == 2:
                V_loading_ltcy += mac_lane * blocknum_col_first * subsum_cnt * weight_loading_latency
                V_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
            else:
                weight_loading_ltcy += mac_lane * blocknum_col_first * subsum_cnt * weight_loading_latency
                weight_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp

            sum_ltcy += mac_lane * blocknum_col_first * subsum_cnt * weight_loading_latency
            sum_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
            cal_ltcy += (blocknum_col_first + 1) * subsum_cnt * cal_latency
            sum_ltcy += blocknum_col_first * (subsum_cnt * cal_latency + max(0, write_back_latency - cal_latency))
            sum_ltcy += (subsum_cnt * cal_latency + max(0, write_back_latency_tmp - cal_latency))
            write_back_ltcy += blocknum_col_first * write_back_latency
            write_back_ltcy += write_back_latency_tmp
            
            idle_core_num[stage_idx] = core_num - core_num_act

            cal_ergy += mac_lane * subsum_cnt * blocknum_col
            gb_read_ergy_IA += subsum_cnt

            if stage_idx == 1:
                gb_read_ergy_K += subsum_cnt * blocknum_col * mac_lane
            elif stage_idx == 2:
                gb_read_ergy_V += subsum_cnt * blocknum_col * mac_lane
            else: 
                gb_read_ergy_weight += subsum_cnt * blocknum_col * mac_lane
                
            gb_write_ergy += (subsum_cnt * mac_num) // mac_lane
            sram_read_ergy += (mac_lane + 1) * subsum_cnt * blocknum_col
            sram_write_ergy += (core_num * subsum_cnt + subsum_cnt * blocknum_col * mac_lane)
        else:
            # 1
            # if a SRAM1 can only hold less than 1 mac_lane of data
            # if subsum_cnt > sram1_height:

            # 1.1
            # a SRAM1 can only hold less than 1 mac_lane of data because 1 mac_lane of data exceeds a SRAM1's capacity
            # this way cal energy and latency should be added with the partial_sum addtion
            # 1.2
            # we chop so slight that a SRAM1 cannot even get a mac_lane col
             
            # number of cores to finish calculating a mac_lane col
            core_num_for_col = math.ceil(subsum_cnt / subsum_sram1)
            if debug_flag == True:
                print("core_num_for_col: " + str(core_num_for_col))
            # number of cores to finish calculating all mac_lane col
            core_num_a_time = core_num_for_col * blocknum_col
            if debug_flag == True:
                print("core_num_a_time: " + str(core_num_a_time))
            if core_num_a_time <= core_num:
                # if we can calculate everything at a time
                if stage_idx == 1:
                    K_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                elif stage_idx == 2:
                    V_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                else:
                    weight_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                sum_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                cal_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency)
                sum_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency) 
                write_back_ltcy += write_back_latency
                sum_ltcy += write_back_latency
                idle_core_num[stage_idx] = core_num - core_num_a_time

            else:
                # if we cannot calculate everything at a time
                if stage_idx == 1:
                    K_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                elif stage_idx == 2:
                    V_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                else:
                    weight_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                sum_ltcy += mac_lane * subsum_sram1 * weight_loading_latency
                cal_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency)
                sum_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency) 
                write_back_ltcy += write_back_latency
                sum_ltcy += write_back_latency

                core_num_act = core_num_a_time - core_num
                if debug_flag == True:
                    print("core_num_act: " + str(core_num_act))

                # if core_num_act > new_bdwidth:
                #     # Demanding GB bandwidth is beyond the bandwidth limit, weight loading latency and write back latency should be more than org
                #     weight_loading_latency_tmp = weight_loading_latency_org * core_num_act / new_bdwidth
                #     write_back_latency_tmp = write_back_latency_org * core_num_act / new_bdwidth
                # else:
                #     weight_loading_latency_tmp = weight_loading_latency_org
                #     write_back_latency_tmp = write_back_latency_org
                weight_loading_latency_tmp = (core_num_act * mac_num) / (new_bandwidth * math.pow(2, 30))
                write_back_latency_tmp = weight_loading_latency_tmp
                
                if stage_idx == 1:
                    K_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency_tmp
                elif stage_idx == 2:
                    V_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency_tmp
                else:
                    weight_loading_ltcy += mac_lane * subsum_sram1 * weight_loading_latency_tmp
                sum_ltcy += mac_lane * subsum_sram1 * weight_loading_latency_tmp
                cal_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency)
                sum_ltcy += subsum_sram1 * cal_latency #+ partial_sum_add_latency * cal_latency) 
                write_back_ltcy += write_back_latency_tmp
                sum_ltcy += write_back_latency_tmp

            cal_ergy += mac_lane * subsum_cnt * blocknum_col
            cal_ergy += blocknum_col * partial_sum_add_energy

            gb_read_ergy_IA += subsum_cnt
            if stage_idx == 1:
                gb_read_ergy_K += subsum_cnt * blocknum_col * mac_lane
            elif stage_idx == 2:
                gb_read_ergy_V += subsum_cnt * blocknum_col * mac_lane
            else: 
                gb_read_ergy_weight += subsum_cnt * blocknum_col * mac_lane

            gb_write_ergy += (subsum_cnt * mac_num) // mac_lane
            sram_read_ergy += (mac_lane + 1) * subsum_cnt * blocknum_col
            sram_write_ergy += core_num * subsum_sram1 + subsum_cnt * blocknum_col * mac_lane

    else:
        # if sram1 cannot hold all partitioned data, this means this stage should be calculated multiple times
        if sram1_height >= subsum_cnt:
            # 3
            # if a SRAM1 can hold more than 1 mac_lane cols of data
            # how many mac_lane col of data can be hold in SRAM1 at a time
            blocknum_col_max = sram1_height // subsum_cnt
            # how many times should it calculates with blocknum_col_max in each core
            times_with_full = blocknum_col // (core_num * blocknum_col_max)
            # how many mac_lane cols remains after times_with_full times calculation
            blocknum_col_remain_all = blocknum_col - times_with_full * core_num * blocknum_col_max
            # how manhy blocks should we assign to some cores at most
            blocknum_col_remain_core = math.ceil(blocknum_col_remain_all / core_num)
            # cores that are still active when computing the last mac_lane col
            core_num_act = blocknum_col_remain_all - (blocknum_col_remain_core - 1) * core_num
            if debug_flag == True:
                print("blocknum_col_max: " + str(blocknum_col_max))
                print("time_with_full: " + str(times_with_full))
                print("blocknum_col_remain_all: " + str(blocknum_col_remain_all))
                print("blocknum_col_remian_core: " + str(blocknum_col_remain_core))
                print("core_num_act: " + str(core_num_act))

            # we need to check the bandwidth here since not all cores need to be assigned data for
            if blocknum_col_remain_all == 0:
                # data can be fully divided with no tail
                if stage_idx == 1:
                    K_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                elif stage_idx == 2:
                    V_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                else:
                    weight_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency

                sum_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                cal_ltcy += times_with_full * blocknum_col_max * subsum_cnt * cal_latency
                sum_ltcy += times_with_full * blocknum_col_max * (subsum_cnt * cal_latency + max(0, write_back_latency - cal_latency))
                write_back_ltcy += times_with_full * blocknum_col_max * write_back_latency

            else:
                # data has a tail
                # if core_num_act > new_bdwidth:
                #     # Demanding GB bandwidth is beyond the bandwidth limit, weight loading latency and write back latency should be more than org
                #     weight_loading_latency_tmp = weight_loading_latency_org * core_num_act / new_bdwidth
                #     write_back_latency_tmp = write_back_latency_org * core_num_act / new_bdwidth
                # else:
                #     weight_loading_latency_tmp = weight_loading_latency_org
                #     write_back_latency_tmp = write_back_latency_org
                weight_loading_latency_tmp = (core_num_act * mac_num) / (new_bandwidth * math.pow(2, 30))
                write_back_latency_tmp = weight_loading_latency_tmp

                if stage_idx == 1:
                    K_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                    K_loading_ltcy += (blocknum_col_remain_core - 1) * mac_lane * subsum_cnt * weight_loading_latency
                    K_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
                elif stage_idx == 2:
                    V_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                    V_loading_ltcy += (blocknum_col_remain_core - 1) * mac_lane * subsum_cnt * weight_loading_latency
                    V_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
                else:
                    weight_loading_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                    weight_loading_ltcy += (blocknum_col_remain_core - 1) * mac_lane * subsum_cnt * weight_loading_latency
                    weight_loading_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp

                sum_ltcy += times_with_full * blocknum_col_max * mac_lane * subsum_cnt * weight_loading_latency
                sum_ltcy += (blocknum_col_remain_core - 1) * mac_lane * subsum_cnt * weight_loading_latency
                sum_ltcy += mac_lane * subsum_cnt * weight_loading_latency_tmp
                cal_ltcy += times_with_full * blocknum_col_max * subsum_cnt * cal_latency
                cal_ltcy += blocknum_col_remain_core * subsum_cnt * cal_latency
                sum_ltcy += (times_with_full * blocknum_col_max + blocknum_col_remain_core - 1) * (subsum_cnt * cal_latency + max(0, write_back_latency - cal_latency))
                sum_ltcy += subsum_cnt * cal_latency + max(0, write_back_latency_tmp - cal_latency)
                write_back_ltcy += (times_with_full * blocknum_col_max + blocknum_col_remain_core - 1) * write_back_latency
                write_back_ltcy += write_back_latency_tmp

            # energy is the same as 2
            cal_ergy += mac_lane * subsum_cnt * blocknum_col
            
            gb_read_ergy_IA += subsum_cnt
            if stage_idx == 1:
                gb_read_ergy_K += subsum_cnt * blocknum_col * mac_lane
            elif stage_idx == 2:
                gb_read_ergy_V += subsum_cnt * blocknum_col * mac_lane
            else: 
                gb_read_ergy_weight += subsum_cnt * blocknum_col * mac_lane

            gb_write_ergy += (subsum_cnt * mac_num) // mac_lane
            sram_read_ergy += (mac_lane + 1) * subsum_cnt * blocknum_col
            sram_write_ergy += (core_num * subsum_cnt + subsum_cnt * blocknum_col * mac_lane)

        else:
            # 4
            # if SRAM1 cannot hold even a mac_lane of data

            # how many cores can complete the calculation of a mac_lane col 
            core_num_col = math.ceil(subsum_cnt / sram1_height)
            # how many subsums can be hold in a core at most
            subsum_core = math.ceil(subsum_cnt / core_num_col)
            if debug_flag == True:
                print("core_num_col: " + str(core_num_col))
                print("subsum_core: " + str(subsum_core))
            
            cal_ergy += (mac_lane * subsum_cnt * blocknum_col + blocknum_col * partial_sum_add_energy) 
            # every round, we need a read of partial sum from gb and a write of partial sum to gb
            rounds = math.ceil(blocknum_col * subsum_cnt / (core_num * subsum_core)) - 1
            
            gb_read_ergy_IA += subsum_cnt
            if stage_idx == 1:
                gb_read_ergy_K += subsum_cnt * blocknum_col * mac_lane
            elif stage_idx == 2:
                gb_read_ergy_V += subsum_cnt * blocknum_col * mac_lane
            else: 
                gb_read_ergy_weight += subsum_cnt * blocknum_col * mac_lane

            gb_write_ergy += ((subsum_cnt * mac_num) // mac_lane + rounds)
            sram_read_ergy += (mac_lane + 1) * subsum_cnt * blocknum_col
            sram_write_ergy += (core_num * subsum_cnt + subsum_cnt * blocknum_col * mac_lane)
            other_ergy += rounds

            # number of cores active in the last round
            core_num_act = core_num_col * blocknum_col - rounds * core_num

            if core_num_act == core_num:
                # rounds is integer, no tail
                rounds += 1
                if debug_flag == True:
                    print("rounds: " + str(rounds))

                if stage_idx == 1:
                    K_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                elif stage_idx == 2:
                    V_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                else:
                    weight_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                sum_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                cal_ltcy += rounds * subsum_core * cal_latency
                sum_ltcy += rounds * (subsum_core * cal_latency + max(0, write_back_latency - cal_latency))
                write_back_ltcy += rounds * write_back_latency
            
            else:
                # rounds is fraction, has tail
                if debug_flag == True:
                    print("rounds: " + str(rounds))
                # if core_num_act > new_bdwidth:
                #     # Demanding GB bandwidth is beyond the bandwidth limit, weight loading latency and write back latency should be more than org
                #     weight_loading_latency_tmp = weight_loading_latency_org * core_num_act / new_bdwidth
                #     write_back_latency_tmp = write_back_latency_org * core_num_act / new_bdwidth
                # else:
                #     weight_loading_latency_tmp = weight_loading_latency_org
                #     write_back_latency_tmp = write_back_latency_org
                weight_loading_latency_tmp = (core_num_act * mac_num) / (new_bandwidth * math.pow(2, 30))
                write_back_latency_tmp = weight_loading_latency_tmp

                if stage_idx == 1:
                    K_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                    K_loading_ltcy += subsum_core * mac_lane * weight_loading_latency_tmp
                elif stage_idx == 2:
                    V_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                    V_loading_ltcy += subsum_core * mac_lane * weight_loading_latency_tmp
                else:
                    weight_loading_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                    weight_loading_ltcy += subsum_core * mac_lane * weight_loading_latency_tmp
                sum_ltcy += rounds * subsum_core * mac_lane * weight_loading_latency
                sum_ltcy += subsum_core * mac_lane * weight_loading_latency_tmp
                cal_ltcy += (rounds + 1) * subsum_core * cal_latency
                sum_ltcy += rounds * (subsum_core * cal_latency + max(0, write_back_latency - cal_latency))
                sum_ltcy += subsum_core * cal_latency + max(0, write_back_latency_tmp - cal_latency)
                write_back_ltcy += rounds * write_back_latency
                write_back_ltcy += write_back_latency_tmp
        
    return([sum_ltcy, cal_ltcy, weight_loading_ltcy, K_loading_ltcy, V_loading_ltcy, write_back_ltcy], [cal_ergy, gb_read_ergy_weight, gb_read_ergy_K, gb_read_ergy_V, gb_read_ergy_IA, gb_write_ergy, sram_read_ergy, sram_write_ergy, other_ergy])

def search_mapping(args):

    """ HW parameters """
    global sram1_height 
    global mac_lane
    global mac_num

    global cal_latency
    global weight_loading_latency
    global write_back_latency
    global new_bandwidth

    frequency = 1.5 * math.pow(10, 9)
    clk_period = 1 / frequency
    die_num = args.die_num 
    core_num_per_die = 16 * 16
    core_num = math.ceil(die_num * core_num_per_die / 8)
    seq_len = args.seq_length
    mac_lane = args.MAC_lane
    mac_num = args.MAC_num
    embedding_dim = args.embedding_dim
    head_num = args.head_num
    head_embedding_dim = embedding_dim // head_num

    sram1_height = args.SRAM_capacity // mac_lane // mac_num
    sram2_height = args.SRAM_capacity // mac_num

    """ 
    Latency & Energy variables & parameters 

    Variables we need to update at every stage:
    cal_ltcy
    config_ltcy
    weight_loading_ltcy
    K_loading_ltcy
    V_loading_ltcy
    write_back_ltcy

    cal_ergy
    config_ergy
    gb_read_ergy_weight
    gb_read_ergy_K
    gb_read_ergy_V
    gb_read_ergy_IA
    gb_write_ergy
    sram_read_ergy
    sram_write_ergy
    other_ergy
    """
    sum_ltcy = 0
    cal_ltcy = 0
    config_ltcy = 0
    weight_loading_ltcy = 0
    K_loading_ltcy = 0
    V_loading_ltcy = 0
    write_back_ltcy = 0
    ltcys = []

    cal_latency = args.cal_latency * clk_period                       # 20ns/hop
    config_latency = args.config_switch_latency * clk_period + die_num * 20 * math.pow(10, -9)
    """ Check GB bandwidth """
    # weight loading latency when GB is offering data to all existing cores
    # when only part of the cores are getting data from GB, the weight loading latency should be calculated like: active_core_num / (sqrt(core_num) * GB_bandwidth)
    new_bandwidth = args.GB_bandwidth * math.sqrt(die_num)
    # latency of transfering a 32B data
    data_amount = mac_num * core_num # in the unit of BYTE
    # print(data_amount)
    # print(new_bandwidth)
    weight_loading_latency = data_amount / (new_bandwidth * math.pow(2, 30))
    write_back_latency = weight_loading_latency
    
    print(f"period: {clk_period}")
    print(f"calculation latency: {cal_latency}")
    print(f"configuration latency: {config_latency}")
    print(f"loading latency: {weight_loading_latency}")
    dump_configs(args)
    if args.debug_flag:
        print("----------------------------------------------")
        print("| GB Latency")
        print("| + weight loading latency: " + str(weight_loading_latency))
        print("| + write back latency: " + str(write_back_latency))
        print("----------------------------------------------")    

    # sum_ergy = 0
    # # when recording, record by times
    # cal_ergy = 0
    # config_ergy = 0
    # gb_read_ergy_weight = 0
    # gb_read_ergy_K = 0
    # gb_read_ergy_V = 0
    # gb_read_ergy_IA = 0
    # gb_write_ergy = 0
    # sram_read_ergy = 0
    # sram_write_ergy = 0
    # other_ergy = 0
    # ergys = []

    # cal_energy = args.cal_energy * utils.METAENERGY / args.MAC_lane
    # config_energy = args.config_switch_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(core_num)
    # gb_read_energy = args.magnification * args.cal_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(core_num)
    # gb_write_energy = args.magnification * args.cal_energy * utils.METAENERGY + args.magnification * 25 * math.sqrt(core_num)
    # sram_read_energy = ((args.magnification * args.cal_energy) / 6) * utils.METAENERGY
    # sram_write_energy = ((args.magnification * args.cal_energy) / 6) * utils.METAENERGY
    # other_energy = gb_read_energy


    """ Data """
    # number of 1 * mac_lane vector in the result vector
    blocknum_col_qkv = math.ceil(embedding_dim / mac_lane)
    blocknum_col_qk = math.ceil(seq_len / mac_lane)
    blocknum_col_av = math.ceil(head_embedding_dim / mac_lane)
    blocknum_col_lp = blocknum_col_qkv
    blocknum_col_fc1 = math.ceil((4 * embedding_dim) / mac_lane)
    blocknum_col_fc2 = blocknum_col_qkv

    # subsum number of activation(a vector)
    subsum_cnt_qkv = math.ceil(embedding_dim / mac_num)
    subsum_cnt_qk = math.ceil(head_embedding_dim / mac_num)
    subsum_cnt_av = math.ceil(seq_len / mac_num)
    subsum_cnt_lp = subsum_cnt_qkv
    subsum_cnt_fc1 = subsum_cnt_qkv
    subsum_cnt_fc2 = math.ceil((4 * embedding_dim) / mac_num)

    if args.debug_flag == True:
        dump_partitions(blocknum_col_qkv, blocknum_col_qk, blocknum_col_av, blocknum_col_lp, blocknum_col_fc1, blocknum_col_fc2, \
                            subsum_cnt_qkv, subsum_cnt_qk, subsum_cnt_av, subsum_cnt_lp, subsum_cnt_fc1, subsum_cnt_fc2)
    # subsum number of weight(a matrix)
    # subsum_cnt_... * blocknum_col = 

    # how many cores are idle at every stage 
    idle_core_num = [0] * 6

    """
    NOTE
    1. haven't consider if vector cannot be hold in SRAM2 at the same time
    2. sram2 should at least hold mac_lane*mac_num data
    """

    if (subsum_cnt_av > sram2_height) or (subsum_cnt_fc2 > sram2_height):
        raise NotImplementedError("Vector cannnot be hold in SRAM2 at the same time!")    
    
    """ Calculating """
    # qkv
    (ltcys, ergys) = analysis(subsum_cnt_qkv, blocknum_col_qkv * 3, core_num, 0, idle_core_num, 0, args.debug_flag)
    # print(ltcys)
    sum_ltcy += ltcys[0]
    cal_ltcy += ltcys[1]
    weight_loading_ltcy += ltcys[2]
    K_loading_ltcy += ltcys[3] 
    V_loading_ltcy += ltcys[4]
    write_back_ltcy += ltcys[5]

    # cal_ergy += ergys[0]
    # gb_read_ergy_weight += ergys[1] 
    # gb_read_ergy_K += ergys[2] 
    # gb_read_ergy_V += ergys[3]
    # gb_read_ergy_IA += ergys[4]
    # gb_write_ergy += ergys[5]
    # sram_read_ergy += ergys[6]
    # sram_write_ergy += ergys[7]
    # other_ergy += ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e1: " + str(ergys[-1]))

    # q*K
    config_ltcy += config_latency
    sum_ltcy += config_latency
    # config_ergy += 1
    
    (ltcys, ergys) = analysis(subsum_cnt_qk, blocknum_col_qk, core_num, 0, idle_core_num, 1, args.debug_flag)

    sum_ltcy += head_num * ltcys[0]
    cal_ltcy += head_num * ltcys[1]
    weight_loading_ltcy += head_num * ltcys[2]
    K_loading_ltcy += head_num * ltcys[3] 
    V_loading_ltcy += head_num * ltcys[4]
    write_back_ltcy += head_num * ltcys[5]

    # cal_ergy += head_num * ergys[0]
    # gb_read_ergy_weight += head_num * ergys[1] 
    # gb_read_ergy_K += head_num * ergys[2] 
    # gb_read_ergy_V += head_num * ergys[3]
    # gb_read_ergy_IA += head_num * ergys[4]
    # gb_write_ergy += head_num * ergys[5]
    # sram_read_ergy += head_num * ergys[6]
    # sram_write_ergy += head_num * ergys[7]
    # other_ergy += head_num * ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e2: " + str(ergys[-1]))

    # a'*V
    config_ltcy += config_latency
    sum_ltcy += config_latency
    # config_ergy += 1

    (ltcys, ergys) = analysis(subsum_cnt_av, blocknum_col_av, core_num, 0, idle_core_num, 2, args.debug_flag)

    sum_ltcy += head_num * ltcys[0]
    cal_ltcy += head_num * ltcys[1]
    weight_loading_ltcy += head_num * ltcys[2]
    K_loading_ltcy += head_num * ltcys[3] 
    V_loading_ltcy += head_num * ltcys[4]
    write_back_ltcy += head_num * ltcys[5]

    # cal_ergy += head_num * ergys[0]
    # gb_read_ergy_weight += head_num * ergys[1] 
    # gb_read_ergy_K += head_num * ergys[2] 
    # gb_read_ergy_V += head_num * ergys[3]
    # gb_read_ergy_IA += head_num * ergys[4]
    # gb_write_ergy += head_num * ergys[5]
    # sram_read_ergy += head_num * ergys[6]
    # sram_write_ergy += head_num * ergys[7]
    # other_ergy += head_num * ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e3: " + str(ergys[-1]))

    # LP
    config_ltcy += config_latency
    sum_ltcy += config_latency
    # config_ergy += 1

    (ltcys, ergys) = analysis(subsum_cnt_lp, blocknum_col_lp, core_num, 0, idle_core_num, 3, args.debug_flag)
    
    sum_ltcy += ltcys[0]
    cal_ltcy += ltcys[1]
    weight_loading_ltcy += ltcys[2]
    K_loading_ltcy += ltcys[3] 
    V_loading_ltcy += ltcys[4]
    write_back_ltcy += ltcys[5]

    # cal_ergy += ergys[0]
    # gb_read_ergy_weight += ergys[1] 
    # gb_read_ergy_K += ergys[2] 
    # gb_read_ergy_V += ergys[3]
    # gb_read_ergy_IA += ergys[4]
    # gb_write_ergy += ergys[5]
    # sram_read_ergy += ergys[6]
    # sram_write_ergy += ergys[7]
    # other_ergy += ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e4: " + str(ergys[-1]))

    # FC1
    config_ltcy += config_latency 
    sum_ltcy += config_latency
    # config_ergy += 1

    (ltcys, ergys) = analysis(subsum_cnt_fc1, blocknum_col_fc1, core_num, 0, idle_core_num, 4, args.debug_flag)

    sum_ltcy += ltcys[0]
    cal_ltcy += ltcys[1]
    weight_loading_ltcy += ltcys[2]
    K_loading_ltcy += ltcys[3] 
    V_loading_ltcy += ltcys[4]
    write_back_ltcy += ltcys[5]

    # cal_ergy += ergys[0]
    # gb_read_ergy_weight += ergys[1] 
    # gb_read_ergy_K += ergys[2] 
    # gb_read_ergy_V += ergys[3]
    # gb_read_ergy_IA += ergys[4]
    # gb_write_ergy += ergys[5]
    # sram_read_ergy += ergys[6]
    # sram_write_ergy += ergys[7]
    # other_ergy += ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e5: " + str(ergys[-1]))

    # FC2
    config_ltcy += config_latency
    sum_ltcy += config_latency
    # config_ergy += 1

    (ltcys, ergys) = analysis(subsum_cnt_fc2, blocknum_col_fc2, core_num, 0, idle_core_num, 5, args.debug_flag)

    sum_ltcy += ltcys[0]
    cal_ltcy += ltcys[1]
    weight_loading_ltcy += ltcys[2]
    K_loading_ltcy += ltcys[3] 
    V_loading_ltcy += ltcys[4]
    write_back_ltcy += ltcys[5]

    # cal_ergy += ergys[0]
    # gb_read_ergy_weight += ergys[1] 
    # gb_read_ergy_K += ergys[2] 
    # gb_read_ergy_V += ergys[3]
    # gb_read_ergy_IA += ergys[4]
    # gb_write_ergy += ergys[5]
    # sram_read_ergy += ergys[6]
    # sram_write_ergy += ergys[7]
    # other_ergy += ergys[8]

    if args.debug_flag:
        for l in ltcys:
            print(str(l))
        print("------")
        for e in ergys:
            print(str(e))

    # print("sram_write_e6: " + str(ergys[-1]))

    """ Metrics updating """
    # cal_ergy = cal_ergy * cal_energy
    # config_ergy = config_ergy * config_energy
    # gb_read_ergy_weight = gb_read_ergy_weight * gb_read_energy
    # gb_read_ergy_K = gb_read_ergy_K * gb_read_energy
    # gb_read_ergy_V = gb_read_ergy_V * gb_read_energy
    # gb_read_ergy_IA = gb_read_ergy_IA * gb_read_energy
    # gb_write_ergy = gb_write_ergy * gb_write_energy
    # sram_read_ergy = sram_read_ergy * sram_read_energy
    # sram_write_ergy = sram_write_ergy * sram_write_energy
    # other_ergy = other_ergy * other_energy
    # sum_ergy = sum([cal_ergy, config_ergy, gb_read_ergy_weight, gb_write_ergy, sram_read_ergy, sram_write_ergy, other_ergy])
    # print(sum_ltcy)
    return (sum_ltcy * math.pow(10, 9), [cal_ltcy, config_ltcy, weight_loading_ltcy, K_loading_ltcy, V_loading_ltcy, write_back_ltcy])
                # sum_ergy, [cal_ergy, config_ergy, gb_read_ergy_weight, gb_read_ergy_K, gb_read_ergy_V, gb_read_ergy_IA, gb_write_ergy, sram_read_ergy, sram_write_ergy, other_ergy], idle_core_num)

def main():
    """ Main function """

    args = argparser().parse_args()
    # print("debug: " + str(args.debug_flag))
    if args.debug_flag == True:
        dump_configs(args)
    (sum_latency, latencys) = search_mapping(args)
    latencys = [i * math.pow(10, 9) for i in latencys]
    # (sum_latency, latencys, sum_energy, energys, idle_core_num) = search_mapping(args)
    # if args.debug_flag == True:
    #     dump_result(sum_latency, latencys, sum_energy, energys)

    # print(str(args.core_num if args.traverse_mode == 1 else args.seq_length) + "," + str(round(sum_latency, 2)) + "," + str(round(sum_energy, 2)) + "," + \
    #         str(round(latencys[0], 2)) + "," + str(round(latencys[1], 2)) + "," + str(round(latencys[2], 2)) + "," + \
    #             str(round(latencys[3], 2)) + "," + str(round(latencys[4], 2)) + "," + str(round(latencys[5], 2)) + "," + \
    #                 str(round(energys[0], 2)) + "," + str(round(energys[1], 2)) + "," + str(round(energys[2], 2)) + "," + str(round(energys[3], 2)) + "," + \
    #                     str(round(energys[4], 2)) + "," + str(round(energys[5], 2)) + "," + str(round(energys[6], 2)) + "," + str(round(energys[7], 2)) + "," + \
    #                         str(round(energys[8], 2)) + "," + str(round(energys[9], 2)))
    idx = [args.die_num, args.seq_length]
    print(str(idx[int(args.traverse_mode) - 1]) + "," + str(round(sum_latency, 2)) + "," + \
        str(round(latencys[0], 2)) + "," + str(round(latencys[1], 2)) + "," + str(round(latencys[2], 2)) + "," + \
            str(round(latencys[3], 2)) + "," + str(round(latencys[4], 2)) + "," + str(round(latencys[5], 2)))
    # print(str(idx[int(args.traverse_mode) - 1]) + "," + str(round(sum_energy, 2)) + "," + \
    #             str(round(energys[0], 2)) + "," + str(round(energys[1], 2)) + "," + str(round(energys[2], 2)) + "," + str(round(energys[3], 2)) + "," + \
    #                 str(round(energys[4], 2)) + "," + str(round(energys[5], 2)) + "," + str(round(energys[6], 2)) + "," + str(round(energys[7], 2)) + "," + \
    #                     str(round(energys[8], 2)) + "," + str(round(energys[9], 2)))
    
    # if args.debug_flag == True:
    #     print(idle_core_num)
    return 0

if __name__ == '__main__':
    main()