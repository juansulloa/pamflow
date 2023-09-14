#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from maad import sound, util
from skimage.feature import peak_local_max


#%%
def spectrogram_local_max_2(
    Sxx, tn, fn, ext,
    min_peak_distance,
    min_peak_amplitude,
    display=False,
):
    # Validate input
    if min_peak_amplitude < Sxx.min():
        raise ValueError(f'Value for minimum peak amplitude is below minimum value on spectrogram')

    # Find peaks in spectrogram
    peaks = peak_local_max(
        Sxx, min_distance=min_peak_distance, threshold_abs=min_peak_amplitude
    )

    if display == True:
        fig, ax = plt.subplots(nrows=1, figsize=(10, 5))
        util.plot_spectrogram(Sxx, ext, log_scale=False, db_range=80, ax=ax)
        ax.scatter(
            tn[peaks[:, 1]],
            fn[peaks[:, 0]],
            marker="o",
            facecolor="none",
            edgecolor="yellow",
        )

    return tn[peaks[:, 1]], fn[peaks[:, 0]] 

#%%
s, fs = sound.load_url('spinetail')
nperseg=512
noverlap=256
db_range=80
min_peak_distance=1
min_peak_amplitude=-50

tp, fp = spectrogram_local_max(
    s, fs, nperseg=512, noverlap=256, db_range=80, min_peak_distance=1, 
    min_peak_amplitude=-50, display=True)

# Compute spectrogram
Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
Sxx_db = util.power2dB(Sxx, db_range=db_range)

tp2, fp2 = spectrogram_local_max_2(
    Sxx_db, tn, fn, ext,
    min_peak_distance=1, min_peak_amplitude=-30, display=True)

np.allclose(tp, tp2)
np.allclose(fp, fp2)