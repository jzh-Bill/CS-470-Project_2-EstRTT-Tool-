"""
author: Zhihao Jin
version: 0.0.1
date: 28/03/2022
purpose: This program will take the host IP address and calculate estimated RTT
and time interval, then plot them on a graph.
"""
from cProfile import label
import shlex, time
from turtle import color
import matplotlib.pyplot as plt
import sys

from subprocess import Popen, PIPE, STDOUT

PROGRAM_RUNNING_TIME = 100

# This function take the command and input on the windows terminal.
def get_simple_cmd_output(cmd, stderr=STDOUT):
    # Execute a simple external command and get its output.
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]

# This function could be configured with specific system check in the future.
# the command line will be different running on different system.
def get_ping_time(host):
    cmd = "ping -n 1 " + host
    flag = False
    rttTime = 0
    while (flag == False):
        # chop up the command line return string and get the RRT value.
        result = str(get_simple_cmd_output(cmd)).replace('\\', '').split(':')[-1].replace("n'", '').replace("-",'').replace("b''", '').split()
        # infinite loop when did not get the returnned string.
        if (result[3].replace("ms,","") == "Received"):
            print("No packet received, trying to ping one more time.")
        else:
            # get the value of RTT
            rttTime = int(result[3].replace("ms,",""))
            flag = True
    return rttTime


# This function will take sampleRTT as parameter and calculate the estimated RTT
# based on the sample RTTs
# And this function will return a list of estimated RTT.
def estimate_RTT_calculator(sampleRTT):
    # -99 is the first element and is used indicates the first time calculation 
    estimate_RTT = [-99]
    for srtt in sampleRTT:
         # this is first calculation
        if estimate_RTT[-1] == -99:
            eRTT = srtt
            estimate_RTT[0] = eRTT
        else:
            eRTT = (1 - 0.125) * estimate_RTT[-1] + 0.125 * srtt 
            estimate_RTT.append(eRTT)

    return estimate_RTT

# This function will take estimated RTT list and sample RTT list as parameters
# and calculate the deviated RTT based on them.
# Finally, return a list of deviated RTT.
def deviated_RTT_calculator(estimateRTTList, sampleRTTList):
    # -99 is the first element and is used indicates the first time calculation 
    devRTT_List = [-99]

    for index in range(len(estimateRTTList)):
        if devRTT_List[-1] == -99:
             # this is first calculation
            devRTT = (1 - 0.25) * 0 + 0.25 * abs(sampleRTTList[index] - estimateRTTList[index])
            devRTT_List[0] = devRTT
        else:
            devRTT = (1 - 0.25) * devRTT_List[-1] + 0.25 * abs(sampleRTTList[index] - estimateRTTList[index])
            devRTT_List.append(devRTT)
    return devRTT_List

# This function will take estimated RTT list and deviated RTT list as parameters
# and calculate the  time interval based on them.
# Finally, return a list of time intervals.
def timeInterval_calculator(estimateRTTList, devRTTLIst):
    timeIntervalList = []
    for index in range(len(estimateRTTList)):
        timeInterval = estimateRTTList[index] + 4 * devRTTLIst[index]
        timeIntervalList.append(timeInterval)
    return timeIntervalList

# This function will take sample RTT list, estimated RTT list, and time interval
# list as parameter and draw the graph.
def plot_graph(sampleRTTList, estimateRTTList, timeIntervalList, host_address):
    
    figure, axis = plt.subplots(1, 2, figsize=(19, 9))
    window_name = "Ploting Graph of Ping to " + host_address
    figure.canvas.set_window_title(window_name)
    # x axis values
    time = []
    for sec in range(1, PROGRAM_RUNNING_TIME + 1, 1):
       time.append(sec)
    
    # configure plot lines 
    axis[0].plot(time, sampleRTTList, label = "Sample RTT", marker='x', markersize=3.5)
    axis[0].plot(time, estimateRTTList, label = "Estimated RTT", marker='x', markersize=3.5)
    axis[0].set(xlabel='Processing Time', ylabel='Time in Milliseconds')
    axis[0].set_title("Estimated RTT")
    axis[0].legend()
    
    axis[1].plot(time, sampleRTTList, label = "Sample RTT", marker='x', markersize=3.5)
    axis[1].plot(time, timeIntervalList, label = "Time Interval RTT", marker='x', color='purple', markersize=3.5)
    axis[1].set(xlabel='Processing Time', ylabel='Time in Milliseconds')
    axis[1].set_title("Time Interval")
    axis[1].legend()

    plt.show()


def main():
    sampleRTTList = []
    estimateRTTList = []
    devRTTLIst = []
    timeIntervalList = []

    host_address = sys.argv[1]

    for sec in range(PROGRAM_RUNNING_TIME, 0, -1):
        rtt = get_ping_time(host_address)
        sampleRTTList.append(rtt)
        print("{0:3} times remaning. And the RTT is {1:6.4f};".format(sec, rtt))
        # Stop the program for 5 seconds
        time.sleep(5)
    print("Plotting now....")

    # calculate the following lists data
    estimateRTTList = estimate_RTT_calculator(sampleRTTList)
    devRTTLIst = deviated_RTT_calculator(estimateRTTList, sampleRTTList)
    timeIntervalList = timeInterval_calculator(estimateRTTList, devRTTLIst)

    plot_graph(sampleRTTList, estimateRTTList, timeIntervalList, host_address)

    # This is sample data printing code.
    # for index in range(len(timeIntervalList)):
    #     print("The sample RTT is: {0:10.8f}, EstRTT is: {1:10.8f}, DevRTT is: {2:10.8f}, TimeInterval is: {3:10.8f}"
    #     .format(sampleRTTList[index], estimateRTTList[index], devRTTLIst[index], timeIntervalList[index]))

main()
