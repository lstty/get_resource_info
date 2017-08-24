#!/usr/bin/python
#coding=utf-8

import os
import json
import time
import urllib,urllib2
import threading

# 用线程实现IO数据更新
def action():
    os.popen("iostat -d -k 1 > /tmp/io_stat")

t = threading.Thread(target=action)
t.start()

time.sleep(10)

while True:
    ################################################ cpu数据 ########################################################
    rs_cpu = os.popen("top -n 1 | grep Cpu  | awk '{print$2,$4,$6,$8,$10,$12,$14,$16}'")

    temp_cpu = {}
    for i in rs_cpu:
        i = i.replace('\n','') # 去掉换行
        temp_cpu = i.split(' ') # 字符串转数组

    # 最终数据字典，添加key
    final_cpu = {}
    final_cpu['us'] = temp_cpu[0]
    final_cpu['sy'] = temp_cpu[1]
    final_cpu['ni'] = temp_cpu[2]
    final_cpu['cpuId'] = temp_cpu[3]
    final_cpu['wa'] = temp_cpu[4]
    final_cpu['hi'] = temp_cpu[5]
    final_cpu['si'] = temp_cpu[6]
    final_cpu['st'] = temp_cpu[7]
    ################################################ cpu数据 ########################################################


    ################################################ 内存数据 ########################################################
    rs_mem = os.popen("free -m | grep Mem | awk '{print$2,$3,$4,$5,$6,$7}'")

    temp_mem = {}
    for i in rs_mem:
        i = i.replace('\n','') # 去掉换行
        temp_mem = i.split(' ') # 字符串转数组

    # 最终数据字典，添加key
    final_mem = {}
    final_mem['total'] = temp_mem[0]
    final_mem['used'] = temp_mem[1]
    final_mem['free'] = temp_mem[2]
    final_mem['shared'] = temp_mem[3]
    final_mem['buffcache'] = temp_mem[4]
    final_mem['available'] = temp_mem[5]
    ################################################ 内存数据 ########################################################


    ################################################ 磁盘数据 ########################################################
    # 获取磁盘使用量，以M为单位,需要考虑有多个分区
    rs = os.popen("df -m | grep '/dev/' | grep -v 'tmpfs' | awk '{print$1,$2,$3,$4,$5,$6}'")

    k_hd = 0
    array_hd = {}
    for i in rs:
        i = i.replace('\n','') # 去除换行符 \n
        array_hd[k_hd] = i.split(' ') # 字符串转列表，空格做分隔符
        k_hd = k_hd + 1

    # 最终数据字典，添加key
    final_disk = {}

    for i in array_hd:
        final_disk[str(i)] = {}
        final_disk[str(i)]['device'] = array_hd[i][0]
        final_disk[str(i)]['size'] = array_hd[i][1]
        final_disk[str(i)]['used'] = array_hd[i][2]
        final_disk[str(i)]['avail'] = array_hd[i][3]
        final_disk[str(i)]['use'] = array_hd[i][4]
        final_disk[str(i)]['mount'] = array_hd[i][5]

    # data_json = json.dumps(final_array) # 数组转json
    ################################################ 磁盘数据 ########################################################


    ################################################ 网络数据 ########################################################
    # 需要考虑有多块网卡
    rs_net = os.popen("cat /proc/net/dev | grep -v -E 'lo|Inter|bytes' | awk '{print $1,$2,$10}'")

    k_net = 0
    array_net = {}
    for i in rs_net:
        i = i.replace('\n','') # 去除换行符 \n
        i = i.replace(':','') # 去除冒号 :
        array_net[k_net] = i.split(' ') # 字符串转列表，空格做分隔符
        k_net = k_net + 1


    final_net = {}
    for i in array_net:
        final_net[str(i)] = {}
        final_net[str(i)]['device'] = array_net[i][0]
        final_net[str(i)]['receive'] = array_net[i][1]
        final_net[str(i)]['send'] = array_net[i][2]
    ################################################ 网络数据 ########################################################


    ################################################ ESTABLISHED状态数据 #############################################
    rs_establish = os.popen("netstat -nat | grep ESTABLISHED | wc -l")
    rs_establish = rs_establish.read()
    final_establish = {}
    final_establish['establish'] = int(rs_establish)
    ################################################ ESTABLISHED状态数据 #############################################


    ###################################################### 磁盘IO ####################################################
    # 需要考虑有多块硬盘
    # tail -n 3, 3由 3 * 硬盘个数 得出
    partition_numb = os.popen("iostat -d -k 1 1 | grep -v -E 'Linux|Device|^$' | awk '{print$1}' | wc -l").read()
    partition_num_int = int(partition_numb) * 3
    partition_num_str = str(partition_num_int)
    rs_io = os.popen("tail -n " + partition_num_str + " /tmp/io_stat | grep -v -E 'Linux|Device|^$' | awk '{print$1,$2,$3,$4,$5,$6}'")

    temp_io = {}
    k_io = 0
    for i in rs_io:
        i = i.replace('\n','') # 去除换行符 \n
        temp_io[k_io] = i.split(' ')
        k_io = k_io + 1

    final_io = {}

    for i in temp_io:
        final_io[str(i)] = {}
        final_io[str(i)]['device'] = temp_io[i][0]
        final_io[str(i)]['tps'] = temp_io[i][1]
        final_io[str(i)]['read'] = temp_io[i][2]
        final_io[str(i)]['write'] = temp_io[i][3]
        final_io[str(i)]['read_all'] = temp_io[i][4]
        final_io[str(i)]['write_all'] = temp_io[i][5]
    ###################################################### 磁盘IO ####################################################


    ################################################ post 数据 #######################################################
    # 组合字典
    final_post = {}
    final_post['cpu'] = final_cpu
    final_post['mem'] = final_mem
    final_post['disk'] = final_disk
    final_post['net'] = final_net
    final_post['establish'] = final_establish #待加入post
    final_post['io'] = final_io #待加入post


    post_data = urllib.urlencode(final_post)
    # post地址
    requrl = "http://xxx.xxx.com/api.php"
    req = urllib2.Request(url = requrl,data = post_data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res
    ################################################ post 数据 #######################################################

    time.sleep(1)

