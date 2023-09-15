#%% Load libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from maad import sound, util
from skimage.feature import peak_local_max
from gs_utils import spectrogram_local_max


#%% Test local max
s, fs = sound.load('/Volumes/lacie_macosx/github/scikit-maad/data/indices/S4A03895_20190522_061500.wav')
nperseg=512
noverlap=256
db_range=80
target_fs=22000
min_peak_distance=1
min_peak_amplitude=-80

# Compute spectrogram
Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
Sxx_db = util.power2dB(Sxx, db_range=db_range)

tp2, fp2 = spectrogram_local_max(
    Sxx_db, tn, fn, ext,
    min_peak_distance, 
    min_peak_amplitude=None,
    threshold_rel=-10, 
    display=True)

#%% Test graphical soundscape
input_data = '/Volumes/lacie_macosx/github/scikit-maad/data/indices/'

graph2 = graphical_soundscape(
    input_data,
    target_fs,
    nperseg,
    noverlap,
    db_range,
    min_peak_distance,
    min_peak_amplitude
)
gs_utils.plot_graph(graph2)
