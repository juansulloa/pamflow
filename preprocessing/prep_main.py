"""
Main script to preprocess audio from passive acoustic monitoring.
The preprocessing step includes:
    - Add prefix to files if needed
    - Get metadata from audio data
    - Identify which sites can be kept for further analysis
    - Take a small sample of the data for further manual analisys

"""
#%% Load libraries
import os
import yaml
import numpy as np
import pandas as pd
from maad import sound, util
from prep_utils import (add_file_prefix, 
                        metadata_summary,
                        plot_sensor_deployment,
                        random_sample_metadata,
                        concat_audio)

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

path_audio = os.path.realpath(config['input_data']['path_audio'])
path_save_metadata_full = config['preprocessing']['path_save_metadata_full']
path_save_metadata_sample = config['preprocessing']['path_save_metadata_sample']

#%% 1. Add file prefix according to file names
flist_changed = add_file_prefix(path_audio, recursive=True, verbose=True)

#%% 2. Get audio metadata and verify acoustic sampling quality
df = util.get_metadata_dir(path_audio, verbose=True)
df.dropna(inplace=True)  # remove problematic files
df['site'] = df.fname.str.split('_').str[0]  # include site column
df.loc[:,'date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')

# Verify acoustic sampling quality
metadata_summary(df)
plot_sensor_deployment(df)

# save dataframes to csv
df.to_csv(path_save_metadata_full, index=False)

#%% 3. Sample audio for overall examination - timelapse soundscapes
sample_len =  config['preprocessing']['sample_len']
idx_date = '2023-05-01'
sample_period = '30T'
path_save = '../../output/figures/'

# select files to create timelapse
df_timelapse = df.loc[df.date_fmt.dt.date == pd.to_datetime(idx_date).date()]
df_timelapse.set_index('date_fmt', inplace=True)

# create time lapse
for site, df_site in df_timelapse.groupby('site'):
    print(site)
    df_site.sort_values('date_fmt', inplace=True)
    df_site = df_site.resample(sample_period).first()
    long_wav, fs = concat_audio(df_site['path_audio'],
                                sample_len=sample_len, 
                                verbose=True)
    sound.write(f'{path_save}{site}_timelapse.wav', fs, long_wav, bit_depth=16)

#%% Check long soundscapes and if necesary make temporal adjustments to audio files
# from prep_utils import rename_files_time_delay
# rename_files_time_delay(path_data_site, delay_hours=-5, verbose=True)

#%% 4.(Optional) Sample audio for manual analisys
peak_hours = ['05', '06', '07', '08', '17', '18', '19', '20']
df_sample = random_sample_metadata(
    df, n_samples_per_site=12, hour_sel=peak_hours, random_state=123)
df_sample.to_csv(path_save_metadata_sample, index=False)