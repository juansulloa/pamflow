"""
Main script to preprocess audio from passive acoustic monitoring.
The preprocessing step includes:
    - Add prefix to files if needed
    - Get metadata from audio data
    - Identify which sites can be kept for further analysis
    - Take a small sample of the data for further manual analisys

"""

import pandas as pd
from maad import util
import yaml
from prep_utils import (add_file_prefix, 
                        metadata_summary,
                        plot_sensor_deployment,
                        random_sample_metadata,
                        concat_audio)

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

path_audio = config['input_data']['path_audio']
path_save_metadata_full = config['preprocessing']['path_save_metadata_full']
path_save_metadata_clean = config['preprocessing']['path_save_metadata_clean']
path_save_metadata_sample = config['preprocessing']['path_save_metadata_sample']

#%% 1. Add file prefix according to file names
add_file_prefix(path_audio, recursive=True)

#%% 2. Get audio metadata and verify acoustic sampling quality
df_full = util.get_metadata_dir(path_audio, verbose=True)
df_full['site'] = df_full.fname.str.split('_').str[0]  # include site column
df_full = df_full.loc[~df_full.sample_rate.isna(),:]  # remove nan values
df_full.loc[:,'date_fmt'] = pd.to_datetime(df_full.date,  format='%Y-%m-%d %H:%M:%S')

# Verify acoustic sampling quality
metadata_summary(df_full)

# Remove sites that have bad configuration
rm_sites = ['CAT003', 'CAT005', 'CAT006', 'CAT012']
df = df_full.loc[~df_full.site.isin(rm_sites),]
plot_sensor_deployment(df)

# save dataframes to csv
df_full.to_csv(path_save_metadata_full, index=False)
df.to_csv(path_save_metadata_clean, index=False)

#%% 3. Sample audio for manual analisys
peak_hours = ['05', '06', '07', '08', '17', '18', '19', '20']
df_sample = random_sample_metadata(
    df, n_samples_per_site=12, hour_sel=peak_hours, random_state=123)
df_sample.to_csv(path_save_metadata_sample, index=False)

#%% 4. Sample audio for overall examination - timelapse soundscapes
df.loc[:,'date_fmt'] = pd.to_datetime(df.loc[:,'date'],  format='%Y-%m-%d %H:%M:%S')
sample_len = 10

# select files to create timelapse
pd.crosstab(df.site, df.date_fmt.dt.hour) # check hours that can be selected in all sites
hours_sel = [0, 5, 6, 12, 19, 23]
df_timelapse = pd.DataFrame()
for site, df_site in df.groupby('site'):
    aux = df_site.loc[df_site['date_fmt'].dt.hour.isin(hours_sel),:]
    aux = aux.groupby(df['date_fmt'].dt.hour, group_keys=False).apply(lambda x: x.sample(1))
    df_timelapse = pd.concat([df_timelapse, aux])

# create time lapse
df_site = df_timelapse.loc[df_timelapse.site=='CAT002',:]
long_wav, fs = concat_audio(df_site['path_audio'], sample_len=10, display=True)
