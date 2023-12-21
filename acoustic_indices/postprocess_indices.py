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
import seaborn as sns

#%%
def plot_acoustic_indices(df, alpha=0.5, size=3):
    # format data
    df.loc[:,'date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df['time'] = df.date.str[11:13].astype(int)
    # plot
    fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
    sns.scatterplot(df, x='time', y='ACI', alpha=alpha, size=size, ax=ax[0,0])
    sns.scatterplot(df, x='time', y='ADI', alpha=alpha, size=size, ax=ax[0,1])
    sns.scatterplot(df, x='time', y='BI', alpha=alpha, size=size, ax=ax[0,2])
    sns.scatterplot(df, x='time', y='H', alpha=alpha, size=size, ax=ax[1,0])
    sns.scatterplot(df, x='time', y='Ht', alpha=alpha, size=size, ax=ax[1,1])
    sns.scatterplot(df, x='time', y='Hf', alpha=alpha, size=size, ax=ax[1,2])
    sns.scatterplot(df, x='time', y='NDSI', alpha=alpha, size=size, ax=ax[2,0])
    sns.scatterplot(df, x='time', y='NP', alpha=alpha, size=size, ax=ax[2,1])
    sns.scatterplot(df, x='time', y='SC', alpha=alpha, size=size, ax=ax[2,2])
    fig.set_tight_layout('tight')

#%% Plot indices to check consistency
df_indices = pd.read_csv('../../output/dataframes_ai/H16_indices.csv')
plot_acoustic_indices(df_indices, alpha=0.3, size=0.5)