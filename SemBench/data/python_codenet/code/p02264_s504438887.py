# coding: utf-8
# Here your code !
import sys
from collections import deque

class CPU():
    def __init__(self, in_quantum):
        self.quantum = in_quantum
        self.total_time = 0
        
    def deal(self, in_process, in_time):
        this_process_time = 0

        if in_time[0] > self.quantum:
            remain_time = in_time[0] - self.quantum
            this_process_time = in_time[0] - remain_time

            in_process.append(in_process[0])
            in_time.append(remain_time)
            
            self.total_time += this_process_time
        else:
            this_process_time = in_time[0]
            self.total_time += this_process_time
            #make log
            self.makeLog(in_process[0])

        in_process.popleft()
        in_time.popleft()
        
        return in_process, in_time

    def makeLog(self, in_process):
        print(in_process, self.total_time)

    
processes = deque()
times = deque()
    
data_cnt, quantum =  list(map(int,input().split(" ")))  

for i in range(data_cnt):
    tmp_process, tmp_time = input().split(" ")
    processes.append(tmp_process)
    times.append(int(tmp_time))

objCPU = CPU(quantum)

while True:
    processes, times = objCPU.deal(processes, times)
    if len(processes) == 0:
        break