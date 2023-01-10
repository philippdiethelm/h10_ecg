#!/usr/bin/python3

import asyncio
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

import numpy as np
import matplotlib.pyplot as plt
from numpy_ringbuffer import RingBuffer
import peakutils

address = "ec:ea:02:85:d9:7a"
PMD_CONTROL = "fb005c81-02e7-f387-1cad-8acd2d8df0c8"
PMD_DATA = "fb005c82-02e7-f387-1cad-8acd2d8df0c8"

display_time_s = 10
sampleRate = 130
deltaT_ns = 1e9 / sampleRate
rb_capacity = int(display_time_s * 1e9 / deltaT_ns)

print(f"Ring buffer capacity: {rb_capacity}")

dt = RingBuffer(capacity=rb_capacity, dtype=np.uint64)
dy = RingBuffer(capacity=rb_capacity, dtype=np.int16)

ot=np.array(1,dtype=np.uint64)
oy=np.array(1,dtype=np.int16)

plt.ion()
ph, = plt.plot(dt, dy)
ph2, = plt.plot(ot, oy, marker="o", ls="", ms=4)    # Peak markers

pa = []

def pmd_control_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    hex = [f"{i:02x}" for i in data]
    print(f"CTRL: {hex}")
    
    # OK
    # CTRL: ['f0', '02', '00', '06', '00']
    #   0xF0 = control point message
    #   0x02 = op_code(Start Measurement)
    #   0x00 = measurement_type(ECG)
    #   0x00 = error(ERROR ALREADY IN STATE)
    #   0x00 = more_frames(false)
    #   0x00 = reserved
    
    # OK (Info)
    # CTRL: ['f0', '02', '00', '00', '00']
    #   0xF0 = control point message
    #   0x02 = op_code(Start Measurement)
    #   0x00 = measurement_type(ECG)
    #   0x00 = error(SUCCESS)
    #   0x00 = more_frames(false)
    #   0x00 = reserved
    
    # Error (MTU too small)
    # CTRL: ['f0', '01', '00', '0a']
    #   0xF0 = control point message
    #   0x01 = op_code(Get Measurement settings)
    #   0x00 = measurement_type(ECG)
    #   0x0a = error(ERROR INVALID MTU)

def pmd_data_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    hex = [f"{i:02x}" for i in data]
    print(f"DATA: {hex}")
    
    # DATA: ['00', '3a', 'd2', '30', '03', 'c2', '4f', '52', '08', '00', '8b', 'ff', 'ff', '99', 'ff', 'ff', 'ae', 'ff', 'ff', 'a9', 'ff', 'ff', 'a7', 'ff', 'ff', 'c0', 'ff', 'ff', 'bb', 'ff', 'ff', '82', 'ff', 'ff', '41', 'ff', 'ff', '34', 'ff', 'ff', '5b', 'ff', 'ff', '7b', 'ff', 'ff', '7d', 'ff', 'ff', '8b', 'ff', 'ff', '9d', 'ff', 'ff', 'ab', 'ff', 'ff', 'c0', 'ff', 'ff', 'd2', 'ff', 'ff', 'd9', 'ff', 'ff', 'e3', 'ff', 'ff', 'e9', 'ff', 'ff', 'f3', 'ff', 'ff', '0b', '00', '00', '19', '00', '00', '14', '00', '00', '1b', '00', '00', '29', '00', '00', '3b', '00', '00', '5c', '00', '00', '77', '00', '00', '85', '00', '00', '8c', '00', '00', '8e', '00', '00', '8a', '00', '00', '73', '00', '00', '4e', '00', '00', '32', '00', '00', '2b', '00', '00', '29', '00', '00', '2b', '00', '00', '3b', '00', '00', '47', '00', '00', '47', '00', '00', '47', '00', '00', '50', '00', '00', '63', '00', '00', '73', '00', '00', '77', '00', '00', '77', '00', '00', '75', '00', '00', '7c', '00', '00', '8a', '00', '00', '95', '00', '00', '95', '00', '00', '8e', '00', '00', '83', '00', '00', '83', '00', '00', '8c', '00', '00', '91', '00', '00', '91', '00', '00', '8a', '00', '00', '7e', '00', '00', '80', '00', '00', '8e', '00', '00', '9a', '00', '00', '9c', '00', '00', '93', '00', '00', '83', '00', '00', '7a', '00', '00', '85', '00', '00', '91', '00', '00', '8c', '00', '00', '6c', '00', '00']
    #   0x00 = ECG
    #   0x3a, 0xd2, 0x30, 0x03, 0xc2, 0x4f, 0x52, 0x08 = timestamp in ns
    #   0x00 = ECG Frame type
    #   0x8b, 0xff, 0xff, sample 0, negative
    #   0x99, 0xff, 0xff,
    #   0xae, 0xff, 0xff,
    #   0xa9, 0xff, 0xff,
    #   0xa7, 0xff, 0xff,
    #   0xc0, 0xff, 0xff,
    #   0xbb, 0xff, 0xff,
    #   0x82, 0xff, 0xff,
    #   0x41, 0xff, 0xff,
    #   0x34, 0xff, 0xff,
    #   0x5b, 0xff, 0xff,
    #   0x7b, 0xff, 0xff,
    #   0x7d, 0xff, 0xff,
    #   0x8b, 0xff, 0xff,
    #   0x9d, 0xff, 0xff,
    #   0xab, 0xff, 0xff,
    #   0xc0, 0xff, 0xff,
    #   0xd2, 0xff, 0xff,
    #   0xd9, 0xff, 0xff,
    #   0xe3, 0xff, 0xff,
    #   0xe9, 0xff, 0xff,
    #   0xf3, 0xff, 0xff,
    #   0x0b, 0x00, 0x00, sample 22, positive
    #   0x19, 0x00, 0x00, 
    #   0x14, 0x00, 0x00,
    #   0x1b, 0x00, 0x00,
    #   0x29, 0x00, 0x00,
    
    if data[0] == 0x00: # 0x00 = ECG
        timestamp = int.from_bytes(data[1:][0:7], byteorder='little', signed=False)
        i = 9
        sample = 0
        deltaT = 1e9/130.0
        # print(f"{timestamp} {deltaT}")
        frame_type = data[i]
        if frame_type == 0: # 0 = ECG Data
            i += 1
            while len(data[i:][0:3]) == 3:
                dt.append(timestamp + sample * deltaT)
                dy.append(int.from_bytes(data[i:][0:2], byteorder='little', signed=True))
                i += 3
                sample += 1
        
        # update line graph data
        dya = np.array(dy)
        dta = np.array(dt)
        ph.set_data(dta, dya)

        # find peaks
        peaks = peakutils.indexes(dya, thres=0.75/max(dya), min_dist=100)

        # mark peaks in graph
        ph2.set_data(dta[peaks], dya[peaks])

        # remove annotations
        for i, a in enumerate(pa):
            a.remove()
        pa[:] = []

        # Calculate HR from peaks
        print(f"# peaks: {len(peaks)}")
        last_i = 0
        for i in range(1, len(peaks)):
            # get interval and calculate HR
            interval = dta[peaks[i]] - dta[peaks[last_i]]
            HR = 60.0*1.0e9/interval
            print(f"Interval: {interval/1.0e6:.1f} ms, HR: {HR:.1f} 1/min")

            # Annotate
            a = plt.annotate(f"{HR:.0f}", xy=(dta[peaks[last_i]] + interval/2, max(dya[peaks[i]], dya[peaks[i]])), ha='center')
            pa.append(a)

            # Next
            last_i = i

        # Update display
        plt.gca().relim()
        plt.gca().autoscale_view()
        plt.pause(0.01)

async def main():
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")
        
        # Register Notifications
        await client.start_notify(PMD_CONTROL, pmd_control_handler)
        await client.start_notify(PMD_DATA, pmd_data_handler)
        
        # Write to PMD control point
        #   0x02 = Start Measurement
        #   0x01 = measurement_type(ECG)
        #   0x00 = setting_type(SAMPLE_RATE)
        #   0x01 = array_length(1)
        #   0x82 0x00 = 130 = 130 Hz
        #   0x01 = setting_type(RESOLUTION)
        #   0x01 = array_length(1)
        #   0x0e = 0x0e 0x00 = 14 = 14 Bits
        await client.write_gatt_char(PMD_CONTROL, bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0e, 0x00]))
        
        # Run for some time
        await asyncio.sleep(15)
        
        # Write to PMD control point
        #   0x03 = Stop Measurement
        #   0x01 = measurement_type(ECG)
        await client.write_gatt_char(PMD_CONTROL, bytearray([0x03, 0x00]))
        
        # Cleanup
        await client.stop_notify(PMD_DATA)
        await client.stop_notify(PMD_CONTROL)

asyncio.run(main())

plt.show(block=True)
