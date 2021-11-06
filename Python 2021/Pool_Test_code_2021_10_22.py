#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PS4824 BLOCK MODE EXAMPLE
# This example opens a 4000a driver device, sets up two channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import csv

# Channel letters to channel numbers
numSwitch = {
    "A":0,
    "B":1,
    "C":2,
    "D":3
}

class ChInfo:

    """Associated info for picoscope channels. """

    def __init__(self, letter):
        self.let = letter
        self.num = numSwitch.get(letter)
        self.b_max = None
        self.adc2mVMax = None

while True: # Stops on no channel input
    channels = []
    print("Stops taking input on empty <CR>")
    while True: # Stops on empty channel input
        ch = input("Trigger channel: ")
        if ch == "":
            break
        ch = ch.upper()
        if ch not in channels:
            channels.append(ChInfo(ch))

    if not channels:
        break # No channel inputs, end program

    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    # Open 4000 series PicoScope
    # Returns handle to chandle for use in future API functions
    status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)

    try:
        assert_pico_ok(status["openunit"])
    except:

        powerStatus = status["openunit"]

        if powerStatus == 286:
            status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])

    # Characteristics shared by channels A-D
    ENABLED = 1
    COUPLING_TYPE = 1 # PS4000a_DC
    CH_RANGE = 8 # PS400a_5V
    ANALOG_OFFSET = 0

    # Set up all channels
    # handle = chandle
    # channel = ch.num
    # enabled = ENABLED
    # coupling type = COUPLING_TYPE
    # range = CH_RANGE
    # analogOffset = ANALOG_OFFSET volts
    for ch in channels:
        status["setCh" + ch] = ps.ps400a
        status["setCh" + ch] = ps.ps4000aSetChannel(chandle, ch.num, ENABLED, COUPLING_TYPE, CH_RANGE, ANALOG_OFFSET)
        assert_pico_ok(status["setCh" + ch])

    threshold = input("Threshold: ")
    DIRECTION = 2 # PS4000a_RISING
    DELAY = 0
    AUTO_TRIGGER = 0
    # Set up single trigger
    # handle = chandle
    # enabled = 1
    # source = channels[0].num
    # threshold = user input
    # direction = DIRECTION
    # delay = 0 s
    # auto Trigger = 0 ms
    status["trigger"] = ps.ps4000aSetSimpleTrigger(chandle, ENABLED, channels[0].num, threshold, DIRECTION, DELAY, AUTO_TRIGGER)
    assert_pico_ok(status["trigger"])

    # Set number of pre and post trigger samples to be collected
    PRE_TRIGGER_SAMPLES = 20000
    POST_TRIGGER_SAMPLES = 60000
    MAX_SAMPLES = PRE_TRIGGER_SAMPLES + POST_TRIGGER_SAMPLES

    # Get timebase information
    # handle = chandle
    # timebase = 8 = timebase
    # noSamples = MAX_SAMPLES
    # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    # pointer to MAX_SAMPLES = ctypes.byref(returnedMaxSamples)
    # segment index = 0
    timebase = 64   #Sample period of 1.24 uS
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(1)
    status["getTimebase2"] = ps.ps4000aGetTimebase2(chandle, timebase, MAX_SAMPLES, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status["getTimebase2"])

    # Run block capture
    # handle = chandle
    # number of pre-trigger samples = PRE_TRIGGER_SAMPLES
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 3 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps4000aIsReady rather than ps4000aBlockReady)
    # pParameter = None
    status["runBlock"] = ps.ps4000aRunBlock(chandle, PRE_TRIGGER_SAMPLES, POST_TRIGGER_SAMPLES, timebase, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps4000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps4000aIsReady(chandle, ctypes.byref(ready))

    SEGMENT_INDEX = 0
    MODE = 0 # PS4000A_RATIO_MODE_NONE

    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = ch.num
    # pointer to buffer max = ctypes.byref(buffer_max)
    # pointer to buffer min = ctypes.byref(buffer_min)
    # buffer length = MAX_SAMPLES
    # segementIndex = SEGMENT_INDEX
    # mode = MODE
    for ch in channels:
        buffer_max = (ctypes.c_int16 * MAX_SAMPLES)()
        ch.b_max = buffer_max
        buffer_min = (ctypes.c_int16 * MAX_SAMPLES)()
        status["setDataBuffers" + ch.let] = ps.ps4000aSetDataBuffers(chandle, ch.num, ctypes.byref(buffer_max), ctypes.byref(buffer_min), MAX_SAMPLES, SEGMENT_INDEX, MODE)
        assert_pico_ok(status["setDataBuffers" + ch.let])

    # create overflow location
    overflow = ctypes.c_int16()
    # create converted type MAX_SAMPLES
    c_max_samples = ctypes.c_int32(MAX_SAMPLES)

    # Retried data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(c_max_samples)
    # downsample ratio = 0
    # downsample ratio mode = PS4000a_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    status["getValues"] = ps.ps4000aGetValues(chandle, 0, ctypes.byref(c_max_samples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    # find maximum ADC count value
    # handle = chandle
    # pointer to value = ctypes.byref(maxADC)
    maxADC = ctypes.c_int16(32767)

    # convert ADC counts data to mV
    for ch in channels:
        ch.adc2VChMax = adc2mV(ch.b_max, CH_RANGE, maxADC)

    # Create time data
    time = np.linspace(0, (c_max_samples.value) * timeIntervalns.value, c_max_samples.value)

    # Plot data
    fig, axs = plt.subplots(len(channels))

    i = 0
    for ch in channels:
        axs[i].plot(time, ch.adc2mVChMax[:])
        axs[i].title.set_text("Channel " + ch.let)
        i = i + 1

    plt.xlabel('Time (ns)')
    plt.ylabel('Voltage (mV)')
    plt.show()

    file_name = input("Input File Name you slimy cunt:")

    new_file = open(file_name,'w')
    new_file.close()
    titles = ["time"]
    for ch in channels:
        titles.append("Channel" + ch.let)

    with open(file_name,'a') as f:
        writer = csv.writer(f)
        writer.writerow(titles)
        writer.writerow(time)
        for ch in channels:
            writer.writerow(ch.adc2mVMax[:])

    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps4000aStop(chandle)
    assert_pico_ok(status["stop"])

    # Close unitDisconnect the scope
    # handle = chandle
    status["close"] = ps.ps4000aCloseUnit(chandle)
    assert_pico_ok(status["close"])

    # display status returns
    print(status)
