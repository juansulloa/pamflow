""" 
Use manual annotations to build a dataset for a specific species

['ENGPUS', 'LEPFRA', 'LEPFUS', 'ORTGAR', 'PITSUL', 'ATRPIL', 
                   'PSEPAR', 'SAKCAN', 'SYNCAN']
"""
import pandas as pd
from maad import sound
import os

#%% TARGET SOUNDS
audio_path = '/Volumes/MANGO/Parex2023/timelapse_10s/'  # path where the audio is located
annot_path = '../../output/dataframes_mannot/compiled_mannot.csv'  # path where annotations are
audio_save_path = '/Volumes/MANGO/Parex2023/3s_dataset/'
target_fs = 48000
segment_len = 3  # segment length in seconds
sp_code = 'LEPFUS'
max_samples = 200

df = pd.read_csv(annot_path)
df = df.loc[df.DET==sp_code,:]

df['length'] = df['End Time (s)'] - df['Begin Time (s)']
df['center'] = df['Begin Time (s)'] + df['length']/2
df['s_ini'] = df['center'] - segment_len/2
df['s_end'] = df['center'] + segment_len/2

try:
    df_sel = df.sample(max_samples, random_state=123)
except:
    df_sel = df

df_sel.reset_index(drop=True, inplace=True)
df_sel['sample_name'] = df_sel.index.astype(str).str.zfill(3) + '.wav'
df_sel.to_csv(os.path.join(audio_save_path, sp_code+'.csv'))

for idx, row in df_sel.iterrows():
    file_path = os.path.join(audio_path, row.fname.replace('.Table.1.selections.txt', '.wav'))
    s, fs = sound.load(file_path)
    s = sound.trim(s, fs, row.s_ini, row.s_end, pad=True)
    s = sound.resample(s, fs, target_fs)
    file_save_path = os.path.join(audio_save_path, sp_code, row.sample_name)    
    try:
        sound.write(file_save_path, target_fs, s, bit_depth=16)
    except:
        os.mkdir(os.path.join(audio_save_path, sp_code))
        sound.write(file_save_path, target_fs, s, bit_depth=16)
    print(f'sample {row.sample_name} saved')

print('Process completed')

#%% OTHER NON-TARGET SOUNDS
audio_path = '/Volumes/lacie_exfat/Parex/timelapse_10s/'  # path where the audio is located
annot_path = '../../output/dataframes_mannot/proportions_species_all.csv' 
audio_save_path = '/Volumes/lacie_exfat/Parex/3s_dataset/'
sp_code = 'OTHER'
max_samples = 500
target_fs = 48000
segment_len = 3  # segment length in seconds

species_to_filter = ['ATRPIL', 'ENGPUS', 'LEPFRA', 'LEPFUS', 'ORTGAR', 'PITSUL',
                   'PSEPAR', 'SAKCAN', 'SYNCAN']

df = pd.read_csv(annot_path)
condition = ~df[species_to_filter].isin([1]).any(axis=1)
df = df[condition]
df['s_ini'] = df['time']
df['s_end'] = df['time'] + segment_len

df_sel = df.sample(max_samples)
df_sel.reset_index(drop=True, inplace=True)
df_sel['sample_name'] = df_sel.index.astype(str).str.zfill(3) + '.wav'
df_sel.to_csv(os.path.join(audio_save_path, sp_code+'.csv'))

for idx, row in df_sel.iterrows():
    file_path = os.path.join(audio_path, row.fname.replace('.Table.1.selections.txt', '.wav'))
    s, fs = sound.load(file_path)
    s = sound.trim(s, fs, row.s_ini, row.s_end, pad=True)
    s = sound.resample(s, fs, target_fs)
    file_save_path = os.path.join(audio_save_path, sp_code, row.sample_name)    
    try:
        sound.write(file_save_path, target_fs, s, bit_depth=16)
    except:
        os.mkdir(os.path.join(audio_save_path, sp_code))
        sound.write(file_save_path, target_fs, s, bit_depth=16)
    print(f'sample {row.sample_name} saved')

#%% GET SAMPLES FOR VALIDATION
