""" Utility functions to compute acoustic indices """

import pandas as pd
from maad import sound, features, util
import os
import seaborn as sns
import matplotlib.pyplot as plt

def compute_acoustic_indices(s, Sxx, tn, fn):
    """
    Parameters
    ----------
    s : 1d numpy array
        acoustic data
    Sxx : 2d numpy array of floats
        Amplitude spectrogram computed with maad.sound.spectrogram mode='amplitude'
    tn : 1d ndarray of floats
        time vector with temporal indices of spectrogram.
    fn : 1d ndarray of floats
        frequency vector with temporal indices of spectrogram..

    Returns
    -------
    df_indices : pd.DataFrame
        Acoustic indices
    """
    
    # Set spectro as power (PSD) and dB scales.
    Sxx_power = Sxx**2
    Sxx_dB = util.amplitude2dB(Sxx)

    # Compute acoustic indices
    ADI = features.acoustic_diversity_index(
        Sxx, fn, fmin=2000, fmax=24000, bin_step=1000, index='shannon', dB_threshold=-70)
    _, _, ACI = features.acoustic_complexity_index(Sxx)
    NDSI, xBA, xA, xB = features.soundscape_index(
        Sxx_power, fn, flim_bioPh=(2000, 20000), flim_antroPh=(0, 2000))
    Ht = features.temporal_entropy(s)
    Hf, _ = features.frequency_entropy(Sxx_power)
    H = Hf * Ht
    BI = features.bioacoustics_index(Sxx, fn, flim=(3000, 11000))
    NP = features.number_of_peaks(Sxx_power, fn, mode='linear', min_peak_val=0, 
                                  min_freq_dist=100, slopes=None, prominence=1e-6)
    _, SC_MF, SC_HF = features.spectral_cover(Sxx_dB, fn, dB_threshold=-80, 
                                              flim_MF=(3000,10000), flim_HF=(10000,20000))
    
    # Structure data into a pandas series
    df_indices = pd.Series({
        'ADI': ADI,
        'ACI': ACI,
        'NDSI': NDSI,
        'BI': BI,
        'Hf': Hf,
        'Ht': Ht,
        'H': H,
        'SC_MF': SC_MF,
        'SC_HF': SC_HF,
        'NP': int(NP)})

    return df_indices

def compute_acoustic_indices_single_file(path_audio):
    s, fs = sound.load(path_audio)    
    s = sound.resample(s, fs, target_fs, res_type='kaiser_fast')

    # Compute the amplitude spectrogram and acoustic indices
    Sxx, tn, fn, ext = sound.spectrogram(
        s, fs, nperseg = 1024, noverlap=0, mode='amplitude')
    df_indices_file = compute_acoustic_indices(s, Sxx, tn, fn)
    df_indices_file['fname'] = os.path.basename(path_audio)
    return df_indices_file

def plot_acoustic_indices(
        df, 
        ai_list=['ADI', 'ACI', 'NDSI', 'BI','Hf', 'Ht', 'H', 'SC', 'NP'], 
        alpha=0.5, 
        size=3):
    
    # format data
    df.loc[:,'date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df['time'] = df.date.str[11:13].astype(int)
    # plot
    fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
    ax = ax.ravel()
    for (i, idx_ax) in enumerate(ax):
        sns.scatterplot(
            df, x='time', y=ai_list[i], alpha=alpha, size=size, ax=idx_ax, legend=False)
        sns.regplot(df, x='time', y=ai_list[i], order=6, scatter=False, ax=idx_ax)

    fig.set_tight_layout('tight')
    