#!/usr/bin/env python3
import os
import numpy as np
import time
from scipy import interpolate, fftpack, signal
from matplotlib import pyplot as plt
from collections import deque
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser


mouse_init= "E7:D4:38:A5:73:CD"


def rssi_fft(timestamp, rssi, N, T):
    # plt.figure()
    # plt.plot(timestamp, rssi)
    # remove DC and calculate FFT 
    yfft = fftpack.fft(rssi - np.mean(rssi))
    xfft = np.linspace(0.0, 1.0 / (2.0 * T), N / 2)
    yfft_scale = 2.0 / N * np.abs(yfft[:N // 2])
    return xfft, yfft_scale
    # plt.figure()
    # plt.plot(xfft, 2.0/N * np.abs(yfft[:N//2]))
    # plt.show()

def rssi_filter(rssi, lowband, T):
    wn = lowband * 2 * T
    [b, a] = signal.butter(4, wn, 'lowpass')
    return signal.filtfilt(b, a, rssi)

def p_open(cmd):
    p_connect = Popen(cmd, shell=True, stdout= PIPE)
    p_connect.wait(10000)
    return p_connect

# load the mac init from the last
try:
    f = open('./mac_init.txt', 'r')
    max_init = f.readline()
    the_first_mac_count = int(max_init, 16)
    f.close()
    if the_first_mac_count >= 255:
        the_first_mac_count = 0
except:
    # save the mac
    f = open('./mac_init.txt', 'w')
    f.write(str(mouse_init[-8:-6]) + "\n")
    time.sleep(1)
    f.close()
    time.sleep(1)
    the_first_mac_count = int(mouse_init[-8:-6]), 16)
    print('[ERROR] mac_init.txt is gone. Initiate the mac_init.txt.')

def into_whitlist(the_first_mac_count):
    tmp = p_open("sudo hcitool lewlclr")
    for i in range(the_first_mac_count, the_first_mac_count + 10):
        max_hex = str(hex(i)).replace('0x', '')
        if len(max_hex)<=1:
            max_hex= '0' + max_hex

        mouse_mac_area = mouse_init[0:9] + max_hex + mouse_init[-6:]
        # print(mouse_mac_area)
        p_open("sudo hcitool lewladd --random " + mouse_mac_area)
    # print("white list init.")

# init
resultlist = list()
devlist = list()
devdict = dict()
fftdict = dict()
# set sample rate to 100Hz, since the max adv frequency for Bluetooth is 50Hz
wint = 4
step = 0.5
T = 0.01

# shell part
# check the mouse is paired?
check_cmd = p_open("echo 'paired-devices \nquit' | bluetoothctl")
cnt = 1000
addr_pair = []
while cnt > 0:
    cnt -= 1
    try:
        line = str(check_cmd.stdout.readline())
        if line.find('paired-devices') > -1:
            line = str(check_cmd.stdout.readline())
            if line.find('[bluetooth]') > -1:
                break
            addr_pair = line.lstrip().rstrip().split(' ')[1]
            print("Find paired mouse, remove it : " + str(addr_pair))

            remove_cmd = "echo 'remove " + str(addr_pair) + "\nquit' | bluetoothctl"
            p_open(remove_cmd)
            print('REMOVED!')
            time.sleep(5)
            break
    except:
        break

p_open("sudo hciconfig hci0 reset")
into_whitlist(the_first_mac_count)
cmdscan = "sudo hcitool lescan --duplicates --whitelist"
p_lescan = Popen(cmdscan, shell=True, stdout=PIPE, stderr=STDOUT)
p_mon = Popen("sudo btmon", shell=True, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

timestamp_prev = 0
caddr = deque()
connected_once = False
connected = False

print('System is Reday! Please set the mouse into adverting mode.')
print('================')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-m", "--mode", help="[fast, slow, near]", dest="mode", required=True)
    args = parser.parse_args()

    if args.mode == 'fast': 
        low = 2.1
        high = 6
        peak = 3.5
    elif args.mode == 'slow':
        low = 1
        high = 1.9
        peak = 4
    elif args.mode == 'near':
        low = 1
        peak = 4
        rssi_peak = -36

    plt.figure(figsize=[5, 6])
    plt.ion()

    while True:
        line = str(p_mon.stdout.readline())
        # print(line)
        if line.find('Remote User Terminated Connection') > -1 or line.find('Disconnect Complete (0x05)') > -1:

            if connected_once:
                connected_once = False
                cnt = 10
                addr_cd = 0
                while cnt > 0:
                    cnt -= 1
                    line = str(p_mon.stdout.readline())
                    # print(line)
                    if line.find('Address') > -1:
                        addr_cd = line.lstrip().rstrip().split(' ')[2]
                        break
                if len(addr_cd) < 6:
                    continue

                print('Device ' + str(addr_cd) + " is disconnecting...")
                remove_cmd = "echo 'remove " + str(addr_cd) + "\nquit' | bluetoothctl"
                p_open(remove_cmd)
                time.sleep(1)

                print('DISCONNECTED!')
                p_open("sudo hciconfig hci0 reset")
                time.sleep(1)

                the_first_mac_count = the_first_mac_count + 1
                into_whitlist(the_first_mac_count)
                p_lescan = Popen(cmdscan, shell=True, stdout=PIPE, stderr=STDOUT)

                print('System is Reday! Please set the mouse into adverting mode.')
                print('================')

            else:
                pass

                # p_lescan.kill()
                # ccc = 100000
                # while p_lescan.poll() is None and ccc > 0:
                #     ccc -= 1
                #     if ccc <= 1:
                #         print("[ERROR] Kill has not been killed.")
                # del p_lescan
                # time.sleep(1)

                # print('System is Reday!')
                # print('================')

        if connected and line[0] == '>' and line.find('dlen 16') > -1:
            connected_once = True
            print("CONNECTED!")
            print('----------------')
            connected = False
            plt.figure(figsize=[5, 6])
            plt.ion()

        elif line[0] == '>' and line.find('plen 33') > -1:
            # if line[0] == '>' and line.find('0x3e)') > -1:
            # print(line)
            try:
                timestamp = float(line.rstrip().split(' ')[-1])
            except:
                continue
            cnt = 0
            flag_skip = 0
            addr = 0
            rssi = 0
            while cnt < 30:
                cnt += 1
                line = str(p_mon.stdout.readline())
                if line.find('Address:') > -1:
                    if line.find('EDR') == -1:
                        try:
                            data = line.lstrip().rstrip().split(':')
                            addr = ' '.join(data[1:6])
                            addr = addr + ' ' + str(data[6].split(' ')[0])
                            addr = addr.lstrip().replace(' ', ':')
                        except:
                            print('[ERROR] addr read error! {}'.format(line))
                            pass
                        continue
                if line.find('NONCONN') > -1:
                    flag_skip = 1
                    break
                if line.find('RSSI') > -1:
                    try:
                        rssi = int(line.lstrip().rstrip().split(' ')[1])
                        break
                        # here is the end of one packet.
                    except:
                        print('rssi read error! {}'.format(line))
                        continue

            # each packet is finished analysis upon, so the algorithm begin.
            if flag_skip == 0:
                # print(addr, rssi, timestamp)
                try:
                    # print(addr, rssi, timestamp)
                    devdict[addr][0].append(rssi)  # 0 is the rssi list
                    devdict[addr][1].append(timestamp)  # 1 is the timestmp list
                    tstart = devdict[addr][1][0]
                    if timestamp - tstart > wint:

                        if timestamp - tstart > 1.5*wint:
                            devdict[addr][0].clear()
                            devdict[addr][1].clear()
                            continue

                        rssis = list(devdict[addr][0])
                        ts = list(devdict[addr][1])
                        # print(ts)
                        fftdict[addr] = ts[-1]

                        # renew the time stamp from 0 and count the data number in step time.
                        timestamps = []
                        cnt_ts = 0
                        for t in ts:
                            timestamps.append(t - ts[0])
                            if t - ts[0] < step:
                                cnt_ts += 1
                        # print(timestamps)
                        # print(cnt_ts)

                        # cal the x data numbers to restore
                        N = int(timestamps[-1] / T)
                        x = np.linspace(0, timestamps[-1], N)

                        # restore the signal with interpolate
                        finterp = interpolate.interp1d(timestamps, rssis)
                        y = finterp(x)
                        y = rssi_filter(y, 10, T)
                        xfft, yfft = rssi_fft(x, y, N, T)
                        yfft_peak = np.max(yfft)
                        yfft_freq = xfft[np.argmax(yfft)]

                        # if timestamp - timestamp_prev > 1:
                        # timestamp_prev = timestamp
                        plt.clf()
                        plt.subplot(211)
                        plt.plot(timestamps, rssis)
                        plt.title("RSSI signal of Mouse:" + str(addr))
                        if args.mode == 'near':
                            plt.xlabel("MAX RSSI signal strength:" + str(np.max(rssi)))
                            plt.plot([0, 4], [rssi_peak, rssi_peak])
                        plt.subplot(212)
                        plt.plot(xfft[0:50], yfft[0:50])
                        if args.mode == 'fast' or args.mode == 'slow':
                            plt.plot([low, low], [0, peak])
                            plt.plot([high, high], [0, peak])
                        elif args.mode == 'near':
                            plt.plot([low, low], [0, peak])
                        plt.title("FFT of the RSSI signal")
                        plt.subplots_adjust(hspace=0.5)
                        plt.pause(0.01)

                        # print("Device %s, freq %.2f, yfft_peak %.2f, mrssi %d"  %
                        #       (addr, yfft_freq, yfft_peak,np.max(rssis)))
                        if args.mode == 'fast' or args.mode == 'slow':
                            condition = (low < yfft_freq < high) and yfft_peak > peak
                        elif args.mode == 'near':
                            condition = (yfft_freq > low) and yfft_peak > peak and np.max(rssis) > rssi_peak
                        if condition:
                            print("Device %s, freq %.2f, yfft_peak %.2f, mrssi %d"  %
                                  (addr, yfft_freq, yfft_peak,np.max(rssis)))
                            print('CONNECTING... ')
                            print('Please wait for pairing... ')
                            caddr.append(addr)
                            del devdict[addr]

                            # save the mac
                            f = open('./mac_init.txt', 'w')
                            f.write(str(addr[-8:-6]) + "\n")
                            time.sleep(1)
                            f.close()
                            time.sleep(1)

                            # # kill the lescan subprocess
                            # p_lescan.kill()
                            # ccc = 100000
                            # while p_lescan.poll() is None and ccc > 0:
                            #     ccc -= 1
                            #     if ccc <= 1:
                            #         print("[ERROR] Kill has not been killed.")
                            # del p_lescan

                            # connect the target mouse
                            for i in range(1000):
                                try:
                                    line = str(p_mon.stdout.readline())
                                    # print(line)
                                except:
                                    break

                            time.sleep(2)
                            connect_cmd = "sudo hcitool lecc --random " + str(addr)
                            p_connect = Popen(connect_cmd, shell=True)

                            try:
                                p_connect.wait(10)
                                connected = True
                            except:
                                print("[ERROR] Connection Failed. Please restart the device into adverting mode.")
                                # p_connect.kill()
                                #
                                # remove_cmd = "echo 'remove " + str(addr) + "\nquit' | bluetoothctl"
                                # p_open(remove_cmd)
                                # time.sleep(1)
                                # p_open("sudo hciconfig hci0 reset")
                                # time.sleep(1)
                                # into_whitlist(the_first_mac_count)
                                # p_lescan = Popen(cmdscan, shell=True, stdout=PIPE)
                                # time.sleep(1)
                                connected = False

                            # plt.ioff()
                            fig = plt.gcf()
                            plt.close("all")

                            # plt.show()

                        # del one step data
                        for i in range(cnt_ts):
                            try:
                                devdict[addr][0].popleft()
                                devdict[addr][1].popleft()
                            except:
                                # print("[ERROR] the pop is wrong.")
                                break

                except KeyError:
                    print("Device {}.".format(addr))
                    rq = deque([rssi])
                    tq = deque([timestamp])
                    devdict[addr] = [rq, tq]
                    fftdict[addr] = timestamp
                except IndexError:
                    print('Index Error')
                    devdict.pop(addr, None)

    # run in bash:     sudo hcitool lescan --duplicates
    # DO NOT use bluetoothctl, since it cannot continously scan even with duplicate-data on
    #
    # bluetoothctl
    # devices
    # remove
    # sudo hciconfig hci0 down
    # service bluetooth restart
    #   sudo hciconfig hci0 up
    # If the pipe stops updating, echo 'remove ' + addr + '\nquit' | bluetoothctl  
