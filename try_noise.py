import os
import serial
import time
import RPi.GPIO as GPIO
import threading
from datetime import datetime
import numpy as np
import sounddevice as sd
import psutil
import gc
import tracemalloc
import objgraph
import logging
import pandas as pd
try:
    with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npz', mmap_mode='r') as z:
         noise = z['noise']
         Fs = int(z['Fs'])
    sd.play(noise, samplerate=Fs, blocking=True)  #sd.wait()
finally:
    sd.stop()
    time.sleep(1)
try:
    with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise_with_ultrasonic.npz', mmap_mode='r') as z:
         noise = z['data']
         Fs = int(z['Fs'])
    sd.play(noise, samplerate=Fs, blocking=True)
finally:
    sd.stop()
    time.sleep(1)
try:
    with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise.npz', mmap_mode='r') as z:
         noise = z['data']
         Fs = int(z['Fs'])
    sd.play(noise, samplerate=Fs, blocking=True)
finally:
    sd.stop()
    time.sleep(1)
try:
    with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise_with_ultrasonic.npz', mmap_mode='r') as z:
         noise = z['data']
         Fs = int(z['Fs'])
    sd.play(noise, samplerate=Fs)
    sd.wait()
finally:
    sd.stop()
    time.sleep(1)
try:
    with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise.npz', mmap_mode='r') as z:
         noise = z['data']
         Fs = int(z['Fs'])
    sd.play(noise, samplerate=Fs)
    sd.wait()
finally:
    sd.stop()
    time.sleep(1)
