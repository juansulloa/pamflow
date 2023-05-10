""" Utilities to compute graphical soundscapes from audio files 

The functions here are a variant of the original graphical soundscapes introduced by Campos-Cerqueira et al. The peaks are detected on the spectrogram instead of detecting peaks on the spectrum. Results are similar but not equal to the ones computed using seewave in R.

References:
  - Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
  - Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
  - Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
"""
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
    """
    Find peaks on spectrogram as coordinate list in time and frequency

    Parameters
    ----------
    s : ndarray
        Audio signal.
    fs : int
        Sample rate of the audio signal.
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
    display : bool, optional
        Option to display the resulting figure.

    Returns
    -------
    fpeaks: pandas Series
        Normalized count of peaks per frequency bin.
    """

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
        s = sound.resample(s, fs, target_fs, res_type="kaiser_fast")
        fpeaks = spectrogram_local_max(
            s,
            target_fs,
            nperseg,
            noverlap,
            db_range,
            min_peak_distance,
            min_peak_amplitude,
        )

        fpeaks = (fpeaks > 0).astype(int)
        fpeaks.name = os.path.basename(df_aux.path_audio)
        res = pd.concat([res, fpeaks.to_frame().T])

    res["time"] = (df.time / 10000).astype(int).to_numpy()

    return res.groupby("time").mean()
