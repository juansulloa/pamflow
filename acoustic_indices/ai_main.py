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
#%%
import os
import yaml
import pandas as pd
from maad import sound
from ai_utils import batch_compute_acoustic_indices, plot_acoustic_indices

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

path_audio = config['input_data']['path_audio']
path_metadata = config['preprocessing']['path_save_metadata_full']
path_save_df = config['acoustic_indices']['path_save_df']
target_fs = config['acoustic_indices']['target_fs']

#%% Load data and flist of selected files
df = pd.read_csv(path_metadata)

#%% Loop through sites
batch_compute_acoustic_indices(df, path_save=path_save_df)

#%% Plot indices to check consistency
df_indices = pd.read_csv('../../output/dataframes_ai/H16_indices.csv')
plot_acoustic_indices(df_indices, alpha=0.3, size=0.5)