""" 
Use manual annotations to build a dataset for a specific species

Myotis sp1: 'MYO_01'
flims = [50000, 70000]
tlen = 0.75

Molossus Molossus: MOLMOL
flims =[30000, 45000]

Sacopterix: SACBIL
flims = [45000, 50000]

"""
import pandas as pd
from maad import sound, rois
import os

#%% TARGET SOUNDS
audio_path = '/Volumes/MANGO/Parex2023/timelapse_10s/'  # path where the audio is located
annot_path = '../../output/dataframes_mannot/compiled_mannot.csv'  # path where annotations are
audio_save_path = '/Volumes/MANGO/Parex2023/3s_dataset_bats/'
target_fs = 192000
segment_len = 0.75  # segment length in seconds
sp_code = 'SACBIL'
max_samples = 200
flims = [30000, 50000]

df = pd.read_csv(annot_path)
df = df.loc[df.DET==sp_code,:]

df_rois = pd.DataFrame()
# Detect sounds in segment
for idx, row in df.iterrows():
    file_path = os.path.join(audio_path, row.fname.replace('.Table.1.selections.txt', '.wav'))
    s, fs = sound.load(file_path)
    s = sound.trim(s, fs, row['Begin Time (s)'], row['End Time (s)'], pad=True)
    segment_detections = rois.find_rois_cwt(s, fs, flims, tlen=0.75, th=0)
    if not segment_detections.empty:
        segment_detections['min_t'] = segment_detections['min_t'] + row['Begin Time (s)']
        segment_detections['max_t'] = segment_detections['max_t'] + row['Begin Time (s)']
        segment_detections['fname'] = file_path
    df_rois = pd.concat([df_rois, segment_detections])
print('Segmentation completed')

df_rois['length'] = df_rois['max_t'] - df_rois['min_t']
df_rois['center'] = df_rois['min_t'] + df_rois['length']/2
df_rois['s_ini'] = df_rois['center'] - segment_len/2
df_rois['s_end'] = df_rois['center'] + segment_len/2

try:
    df_sel = df_rois.sample(max_samples)
except:
    df_sel = df_rois

df_sel.reset_index(drop=True, inplace=True)
df_sel['sample_name'] = df_sel.index.astype(str).str.zfill(3) + '.wav'
df_sel.to_csv(os.path.join(audio_save_path, sp_code+'.csv'))

# write audio
for idx, row in df_sel.iterrows():
    file_path = os.path.join(audio_path, row.fname.replace('.Table.1.selections.txt', '.wav'))
    s, fs = sound.load(file_path)
    s = sound.trim(s, fs, row.s_ini, row.s_end, pad=True)
    file_save_path = os.path.join(audio_save_path, sp_code, row.sample_name)    
    try:
        sound.write(file_save_path, 48000, s, bit_depth=16)
    except:
        os.mkdir(os.path.join(audio_save_path, sp_code))
        sound.write(file_save_path, 48000, s, bit_depth=16)
    print(f'sample {row.sample_name} saved')

print('All samples saved to folder', audio_save_path)

#%% OTHER NON-TARGET SOUNDS
audio_path = '/Volumes/MANGO/Parex2023/timelapse_10s/'  # path where the audio is located
annot_path = '../../output/dataframes_mannot/proportions_species_all.csv' 
audio_save_path = '/Volumes/MANGO/Parex2023/3s_dataset_bats/'
sp_code = 'OTHER'
max_samples = 300
target_fs = 192000
segment_len = 0.75  # segment length in seconds

species_to_filter = ['MOLMOL', 'SACBIL', 'MYO_01']

df = pd.read_csv(annot_path)
condition = ~df[species_to_filter].isin([1]).any(axis=1)
df = df[condition]
df['s_ini'] = df['time']
df['s_end'] = df['time'] + segment_len

df_sel = df.sample(max_samples, random_state=123)
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

#%% Remove noisy labels

path_audio = '/Volumes/MANGO/MYO/MYO_01/'
rm_data = pd.read_csv('/Volumes/MANGO/MYO/MYO_01.csv', sep=',')
rm_data.keep.value_counts()
rm_data = rm_data.loc[(rm_data.keep==True),:]['sample_name']

for fname in rm_data.to_list():
    fname_rm = os.path.join(path_audio, fname)
    os.remove(fname_rm)

print('Files removed')

#%% Get new data for manual expert validation
df_detections = pd.read_csv('../../output/detections/bat_detections_compiled.csv')
df_metadata = pd.read_csv('../../output/metadata/metadata_t0-t1-t2.csv')
audio_save_path = '/Volumes/MANGO/tmp_2/'
audio_path = '/Volumes/MANGO/Parex2023/selected_data_bats/'

df_detections = df_detections.merge(df_metadata, on='fname')
df_detections = df_detections.loc[df_detections['Species Code']=='MYO_01']
df_detections = df_detections.loc[df_detections['Confidence']>0.5]

df_sel = df_detections.sample(500, random_state=123)
df_sel = df_sel[['path_audio', 'fname', 'Begin Time (s)', 'End Time (s)']]
df_sel.reset_index(drop=True, inplace=True)
df_sel['sample_name'] = 'X' + df_sel.index.astype(str).str.zfill(3) + '.wav'
df_sel.to_csv(os.path.join(audio_save_path, 'MYO_01.csv'))

for idx, row in df_sel.iterrows():
    file_path = os.path.join(audio_path, row.fname)
    s, fs = sound.load(file_path)
    s = sound.trim(s, fs, row['Begin Time (s)'], row['End Time (s)'], pad=True)
    file_save_path = os.path.join(audio_save_path, row.sample_name) 
    sound.write(file_save_path, fs, s, bit_depth=16)
    print(f'sample {row.sample_name} saved')
