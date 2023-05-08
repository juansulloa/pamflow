"""
Graphical soundscape with local maxima
WARNING: THIS SCRIPT IS UNDER CONSTRUCTION

"""
import pandas as pd
import yaml
import os
import numpy as np
from maad import sound, util
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

path_audio = config['input_data']['path_audio']
path_metadata = config['preprocessing']['path_save_metadata_clean']
db_range = 80
min_peak_amplitude = 20
display =False

#%%
df = pd.read_csv(path_metadata)
flist = df.loc[df['site']=='CAT011',:]['path_audio'].to_list()

res = pd.DataFrame()
for idx, fname in enumerate(flist):
    print(idx, '/', len(flist), ':' ,os.path.basename(fname))
    # Load data
    s, fs = sound.load(fname)
    s = sound.resample(s, fs, target_fs=48000, res_type='kaiser_fast')

    # Compute spectrogram
    Sxx, tn, fn, ext = sound.spectrogram(s, 48000, nperseg = 256, noverlap=128)
    Sxx_db = util.power2dB(Sxx, db_range=db_range) + db_range
    
    # Find peaks in spectrogram
    peaks = peak_local_max(Sxx_db, min_distance=20, threshold_abs=min_peak_amplitude)
    
    # Organize output
    times, freqs = peaks[:,1], peaks[:,0]
    freq_idx, count_freq = np.unique(freqs, return_counts=True)
    count_peak = np.zeros(fn.shape)
    count_peak[freq_idx] = count_freq
    fpeaks = pd.Series(index=fn, 
                       data= count_peak)

    if display==True:
        fig, ax = plt.subplots(nrows=1, figsize=(10, 5))
        ax.imshow(Sxx_db, cmap='gray', aspect='auto', origin='lower', extent=ext)
        ax.scatter(tn[peaks[:,1]], fn[peaks[:,0]], 
                   marker='o', facecolor='none', edgecolor='yellow')

    
    fpeaks.name = os.path.basename(fname)
    res = pd.concat([res, fpeaks.to_frame().T])



plt.close('all')
plt.imshow(np.log1p(res.values.T), aspect='auto', origin='lower')

res['time'] = res.index.str[-10:-8].astype(int)
res_mean = res.groupby('time').mean()
plt.close('all')
plt.imshow(res_mean.values.T, aspect='auto', origin='lower')
