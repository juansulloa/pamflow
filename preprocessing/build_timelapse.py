""" 
Build time lapse soundscapes to evaluate data
"""
import yaml
import numpy as np
import pandas as pd
from maad import sound
from prep_utils import concat_audio

#%% Set variables
# Open the config file and load its contents into a dictionary
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

path_audio = config["input_data"]["path_audio"]
path_metadata = config["preprocessing"]["path_save_metadata_t1"]
sample_len = 1
site_sel = 'Z3-G094'

#%% Sample audio for overall examination - timelapse soundscapes
df = pd.read_csv(path_metadata)
df_timelapse = df.groupby('site').get_group(site_sel)
df_timelapse.sort_values('fname', inplace=True)

# create time lapse
for day, df_site in df_timelapse.groupby('day'):
    print(day)
    long_wav, fs = concat_audio(df_site['path_audio'],
                                sample_len=sample_len, 
                                verbose=True,
                                display=False)
    long_wav = sound.resample(long_wav, fs, target_fs=48000)
    sound.write('../../output/figures/'+site_sel+'_'+day+'_timelapse.wav', 48000, long_wav, bit_depth=16)