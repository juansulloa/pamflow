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

import os
import yaml
import pandas as pd
from maad import sound
from ai_utils import compute_acoustic_indices, plot_acoustic_indices

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

path_audio = config['input_data']['path_audio']
path_metadata = config['preprocessing']['path_save_metadata_full']
path_save_df = config['acoustic_indices']['path_save_df']
target_fs = config['acoustic_indices']['target_fs']

#%% Load data and flist of selected files
flist = pd.read_csv(path_metadata)
sensor_list = flist.sensor_name.unique()

#%% Loop through sites
for sensor_name in sensor_list:
    flist_sel = flist.loc[flist.sensor_name==sensor_name,:]
        
    df_indices = pd.DataFrame()
    for idx_row, row in flist_sel.iterrows():
        print(f'{idx_row+1} / {flist_sel.index[-1]}: {row.fname}', end='\r')
        # Load and resample to 48 kHz
        s, fs = sound.load(row.path_audio)
        s = sound.resample(s, fs, target_fs, res_type='scipy_poly')
    
        # Compute the amplitude spectrogram and acoustic indices
        Sxx, tn, fn, ext = sound.spectrogram(
            s, target_fs, nperseg = 1024, noverlap=0, mode='amplitude')
        df_indices_file = compute_acoustic_indices(s, Sxx, tn, fn)
            
        # add file information to dataframes
        add_info = row[['fname', 'sensor_name', 'date']]
        df_indices_file = pd.concat([add_info, df_indices_file])
        
        # append to dataframe
        df_indices = pd.concat([df_indices, df_indices_file.to_frame().T])
        
    # Save dataframes
    df_indices.to_csv(path_save_df+sensor_name+'_indices.csv', index=False)

#%% Plot indices to check consistency
df_indices = pd.read_csv('../../output/dataframes_ai/P2-G087_indices.csv')
plot_acoustic_indices(df_indices, alpha=0.3, size=0.5)