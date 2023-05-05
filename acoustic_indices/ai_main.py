#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute acoustic indices on a list of files.

The audio file is first resampled to 48 kHz.
Acoustic indices computed include:
    - Acoustic Diversity Index (ADI)
    - Acoustic Complexity Index (ACI)
    - Acoustic Space Used (ASU)
    - Normalized Difference Soundscape Index (NDSI)
    - Bioacoustic Index (BI)
    - Acoustic Entropy Index (H)
    - Number of peaks (NP)
    - Spectral cover (SC)

"""

import pandas as pd
import os
from maad import sound
from ai_utils import compute_acoustic_indices

#%% Set variables
path_flist_sel = '/Volumes/lacie_exfat/Cataruben/metadata/metadata_clean.csv'
path_audio = '/Volumes/lacie_exfat/Cataruben/audio/'
path_save_df = './dataframes/'
target_fs = 48000  # if resample is needed

#%% Load data and flist of selected files
flist = pd.read_csv(path_flist_sel)
sensor_list = flist.sensor_name.unique()

#%% Loop through sites
for sensor_name in sensor_list:
    flist_sel = flist.loc[flist.sensor_name==sensor_name,:]
        
    df_indices = pd.DataFrame()
    for idx_row, row in flist_sel.iterrows():
        print(idx_row+1, '/', flist_sel.index[-1], ':', row.fname)
        # Load and resample to 48 kHz
        s, fs = sound.load(os.path.join(path_audio, row.path_audio))
        s = sound.resample(s, fs, target_fs, res_type='kaiser_fast')
    
        # Compute the amplitude spectrogram and acoustic indices
        Sxx, tn, fn, ext = sound.spectrogram(
            s, target_fs, nperseg = 1024, noverlap=0, mode='amplitude')
        df_indices_file = compute_acoustic_indices(s, Sxx, tn, fn)
            
        # add file information to dataframes
        add_info = row[['fname', 'sensor_name', 'date']]
        df_indices_file = pd.concat([add_info, df_indices_file])
        
        # append to dataframe
        df_indices = pd.concat([df_indices, df_indices_file.to_frame().T])
        #df_indices = df_indices.append(df_indices_file, ignore_index=True)
        
    # Save dataframes
    df_indices.to_csv(path_save_df+sensor_name+'_indices.csv', index=False)

#%% Plot indices to check consistency
