""" 
Copy the list of files to a new location to facilitate the analisys

"""
import pandas as pd
import shutil
import os
from maad import sound

# List of file names you want to copy
file_list = pd.read_csv('../../output/metadata/metadata_t0-t1-t2.csv')

# Source directory
source_directory = "/Volumes/MANGO/Parex2023/"

# Destination directory
destination_directory = "/Volumes/MANGO/Parex2023/selected_data/"

# Ensure the destination directory exists, create it if necessary
os.makedirs(destination_directory, exist_ok=True)

# Iterate over the file list and copy each file
for file_name in file_list['path_audio'].to_list():
    source_path = file_name
    destination_path = file_name.replace('Parex2023/', 'Parex2023/selected_data/')
    try:
        shutil.copy2(source_path, destination_path)
        print(f"Successfully copied {file_name} to {destination_directory}")
    except FileNotFoundError:
        print(f"File {file_name} not found in {source_directory}")
    except PermissionError:
        print(f"Permission error: Unable to copy {file_name}")

print("Copy process completed.")

#%% Copy data for bats

# List of file names you want to copy
flist = pd.read_csv('../../output/metadata/metadata_t0-t1-t2.csv')
path_save_audio = '/Volumes/MANGO/Parex2023/selected_data_bats_32k/'
target_fs = 32000

night_hours = [17, 18, 19, 20, 21, 22, 23, 0, 1, 2,3 ,4, 5, 6, 7]
flist['day_period'] = 'day'
flist.loc[flist.hour.isin(night_hours),'day_period'] = 'night'
flist = flist.loc[flist.day_period=='night',:]

for fname in flist.path_audio.to_list():
    try:
        s, fs = sound.load(fname)
        fname_save = os.path.join(path_save_audio, os.path.basename(fname))
        sound.write(fname_save, target_fs, s, bit_depth=16)
    except:
        print(fname)

