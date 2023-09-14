#%% Load libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from maad import sound, util
from skimage.feature import peak_local_max


#%%
def spectrogram_local_max(
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
def graphical_soundscape(
    df, target_fs, nperseg, noverlap, db_range, min_peak_distance, min_peak_amplitude
):
    """
    Computes a graphical soundscape from a given dataframe of audio files.

    Parameters
    ----------
    df : pandas DataFrame
        A Pandas DataFrame containing information about the audio files. The dataframe needs to have the columns 'path_audio' and 'time'.
    target_fs : int
        The target sample rate to resample the audio signal if needed.
    nperseg : int
        Window length of each segment to compute the spectrogram.
    noverlap : int
        Number of samples to overlap between segments to compute the spectrogram.
    db_range : float
        Dynamic range of the computed spectrogram.
    min_peak_distance : int
        Minimum number of indices separating peaks.
    min_peak_amplitude : float
        Minimum amplitude threshold for peak detection in decibels.

    Returns
    -------
    res : pandas DataFrame
        A Pandas DataFrame containing the graphical representation of the soundscape.
    """
    res = pd.DataFrame()
    for idx, df_aux in df.iterrows():
        print(idx + 1, "/", len(df), ":", os.path.basename(df_aux.fname))
        
        # Load data
        s, fs = sound.load(df_aux.path_audio)
        s = sound.resample(s, fs, target_fs, res_type="scipy_poly")
        Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
        Sxx_db = util.power2dB(Sxx, db_range=db_range)

        # Compute local max
        peak_time, peak_freq = spectrogram_local_max(
            Sxx_db, tn, fn, ext,
            min_peak_distance, 
            min_peak_amplitude)
        
        # Count number of peaks at each frequency bin
        freq_idx, count_freq = np.unique(peak_freq, return_counts=True)
        count_peak = np.zeros(fn.shape)
        bool_index = np.isin(fn, freq_idx)
        indices = np.where(bool_index)[0]
        count_peak[indices] = count_freq / len(tn)
        peak_density = pd.Series(index=fn, data=count_peak)

        # Normalize per time
        #peak_density = (peak_density > 0).astype(int)
        peak_density.name = os.path.basename(df_aux.path_audio)
        res = pd.concat([res, peak_density.to_frame().T])

    res["time"] = (df.time / 10000).astype(int).to_numpy()

    return res.groupby("time").mean()

#%%
s, fs = sound.load_url('spinetail')
nperseg=512
noverlap=256
db_range=80
min_peak_distance=1
min_peak_amplitude=-50

# Compute spectrogram
Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
Sxx_db = util.power2dB(Sxx, db_range=db_range)

tp2, fp2 = spectrogram_local_max(
    Sxx_db, tn, fn, ext,
    min_peak_distance=1, min_peak_amplitude=-30, display=True)