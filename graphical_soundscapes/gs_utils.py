import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from maad import sound, util
from skimage.feature import peak_local_max


def spectrogram_local_max(
    s,
    fs,
    nperseg,
    noverlap,
    db_range,
    min_peak_distance,
    min_peak_amplitude,
    display=False,
):
    # Compute spectrogram
    Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
    Sxx_db = util.power2dB(Sxx, db_range=db_range) + db_range

    # Find peaks in spectrogram
    peaks = peak_local_max(
        Sxx_db, min_distance=min_peak_distance, threshold_abs=min_peak_amplitude
    )

    # Count number of peaks at each frequency bin and normalize per time
    times, freqs = peaks[:, 1], peaks[:, 0]
    freq_idx, count_freq = np.unique(freqs, return_counts=True)
    count_peak = np.zeros(fn.shape)
    count_peak[freq_idx] = count_freq / len(tn)
    fpeaks = pd.Series(index=fn, data=count_peak)

    if display == True:
        fig, ax = plt.subplots(nrows=1, figsize=(10, 5))
        ax.imshow(Sxx_db, cmap="gray", aspect="auto", origin="lower", extent=ext)
        ax.scatter(
            tn[peaks[:, 1]],
            fn[peaks[:, 0]],
            marker="o",
            facecolor="none",
            edgecolor="yellow",
        )

    return fpeaks

def graphical_soundscape(
        df, target_fs, nperseg, noverlap, db_range, min_peak_distance, min_peak_amplitude):
    res = pd.DataFrame()
    for idx, df_aux in df.iterrows():
        print(idx+1, '/', len(df), ':' ,os.path.basename(df_aux.fname))
        # Load data
        s, fs = sound.load(df_aux.path_audio)
        s = sound.resample(s, fs, target_fs, res_type='kaiser_fast')
        fpeaks = spectrogram_local_max(
            s, target_fs, nperseg, noverlap, db_range, min_peak_distance, min_peak_amplitude)

        fpeaks = (fpeaks > 0).astype(int)
        fpeaks.name = os.path.basename(df_aux.path_audio)
        res = pd.concat([res, fpeaks.to_frame().T])

    res['time'] = (df.time/10000).astype(int).to_numpy()

    return res.groupby('time').mean()
