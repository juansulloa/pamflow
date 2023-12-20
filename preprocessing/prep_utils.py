#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import os
import argparse
import shutil
import pandas as pd
import numpy as np
import glob
from pathlib import Path
from os import listdir
from maad import sound, util
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------
# Main Utilities For Other Functions
# ----------------------------------

# Function argument validation
def input_validation_df(df):
    """ Validate dataframe or path input argument """
    if isinstance(df, pd.DataFrame):
        pass
    elif isinstance(df, str):
        try:
            # Attempt to load a DataFrame from the provided file path.
            df = pd.read_csv(df) 
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {df}")
    else:
        raise ValueError("Input 'data' must be either a Pandas DataFrame, a file path string, or None.")
    return df

#%%
# ------------------------
# Visualization Functions
# ------------------------
def plot_sensor_deployment(df, ax=None):
    """ Plot sensor deployment to have an overview of the sampling

    Parameters
    ----------
    df : pandas DataFrame
        The dataframe must have the columns site, date, sample_length.
        Use maad.util.get_audio_metadata to compile the dataframe.
    ax : matplotlib.axes, optional
        Matplotlib axes fot the figure, by default None

    Returns
    -------
    matplotlib.figure
        If axes are not provided, a figure is created and figure handles are returned.
    """
    # Function argument validation
    df = input_validation_df(df)

    df['date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df_out = pd.DataFrame()
    for sensor_name, df_sensor in df.groupby('sensor_name'):
        aux = pd.DataFrame(df_sensor.date_fmt.dt.date.value_counts())
        aux['sensor_name'] = sensor_name
        aux.reset_index(inplace=True)
        aux.rename(columns={'index': 'date', 'date_fmt': 'num_rec'}, inplace=True)
        df_out = pd.concat([df_out, aux], axis=0)

    df_site = pd.DataFrame()
    for sensor_name, df_sensor in df.groupby('sensor_name'):
        df_sensor.sort_values('date', inplace=True)
        site_info = pd.DataFrame({
            'sensor_name': sensor_name,
            'sample_rate': int(df_sensor.sample_rate.iloc[0]),
            'bit_depth': int(df_sensor.bits.iloc[0]),
            'date_ini': df_sensor.date.iloc[0][0:10],
            'date_end': df_sensor.date.iloc[-1][0:10],
            'time_ini': df_sensor.date.iloc[0][11:19],
            'time_end': df_sensor.date.iloc[-1][11:19]
            }, index=[sensor_name])
        df_site = pd.concat([df_site, site_info], ignore_index=True)

    if ax == None:
        sns.scatterplot(y='date', x='sensor_name', 
                        size='num_rec', size_norm = (10, 100), 
                        hue='num_rec', hue_norm = (10, 100),
                        data=df_out)
        plt.show()
    else:
        sns.scatterplot(y='date', x='sensor_name', 
                        size='num_rec', size_norm = (10, 100), 
                        hue='num_rec', hue_norm = (10, 100),
                        data=df_out, ax=ax)

#%%
# ------------------------
# File Managment Functions
# ------------------------
def search_files(directory=".", extension=""):
    """
    Search for files within a specified directory and its subdirectories.

    Args:
        directory (str, optional): The directory to start the search in (default: current directory).
        extension (str, optional): The file extension to filter by (e.g., ".txt"). If provided, only files with
            this extension will be considered. If not provided or an empty string, all files will be considered.

    Returns:
        str or None: The path to the first matching file found, or None if no matching file is found.

    Note:
        This function uses a recursive approach to search for files in the specified directory and its subdirectories.
        It returns the path to the first matching file it encounters during the search.
    """
    extension = extension.lower()
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                return os.path.join(dirpath, name)
            elif not extension:
                return os.path.join(dirpath, name)

def listdir_pattern(path_dir, ends_with=None):
    """
    Wraper function from os.listdir to include a filter to search for patterns
    
    Parameters
    ----------
        path_dir: str
            path to directory
        ends_with: str
            pattern to search for at the end of the filename
    Returns
    -------
    """
    flist = listdir(path_dir)

    new_list = []
    for names in flist:
        if names.endswith(ends_with):
            new_list.append(names)
    return new_list


import glob
import os
import time

#%%
def find_wav_files(folder_path, recursive=False):
    """ Search for files with wav or WAV extension """
    wav_files = []
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.wav'):
                    wav_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(folder_path):
                    if file.lower().endswith('.wav'):
                        wav_files.append(os.path.join(folder_path, file))
    
    # Transform the list of strings to a list of Path objects
    wav_files = [Path(path) for path in wav_files]
    
    return wav_files

#%%
def add_file_prefix(folder_name: str, recursive:bool=False, verbose:bool=False) -> None:
    """
    Adds a prefix to the file names in the given directory.
    The prefix is the name of the immediate parent folder of the files.

    Parameters:
    folder_name(str): Name of directory which contains files.
    recursive(bool): If True, searches for files in sub-directories recursively.
                     Defaults to False if not provided.

    Returns: None
    """
    folder_path = Path(folder_name)

    # Get list of files to process
    flist = find_wav_files(folder_path, recursive=recursive)
    
    # remove hidden files 
    flist = [f for f in flist if not f.name.startswith('.')]

    if verbose:
        print(f'Number of WAVE files detected: {len(flist)}')

    # remove files that already have the parent directory name
    flist = [f for f in flist if (not f.name.startswith(f.parent.name+'_'))]

    # Loop and change names
    flist_changed = list()
    for fname in flist:
        prefix = fname.parent.name
        new_fname = fname.with_name(f'{prefix}_{fname.name}')
        try:
            fname.rename(new_fname)
            flist_changed.append(str(new_fname))
        except Exception as e:
            print(f"Error occurred while renaming {fname}: {e}")
    
    if verbose:
        print(f'Number of WAVE files detected with no prefix: {len(flist)}')
        print(f'Number of WAVE files renamed: {len(flist_changed)}')
        
    return flist_changed

def copy_file_list(flist, path_save):
    """ Copy selected files to a new folder """
    for _, row in flist.iterrows():
        src_file = row.path_audio
        dst_file = path_save + row.fname
        shutil.copyfile(src_file, dst_file)

def rename_files_time_delay(path_dir, delay_hours=-5, verbose=False):
    """ Rename files to fix time delay issues
    When using audio recorders, time can be badly configured. This simple function allows to fix time dalys that occurr because of changes in time zones. The files must have a standard format.

    """
    if type(path_dir) == str:
        flist = glob.glob(os.path.join(path_dir, '*.WAV'))
        flist.sort()

    for fname in flist:
        fname_orig = util.filename_info(fname)
        date_orig = pd.to_datetime(fname_orig['date'])
        fname_ext = '.' + fname_orig['fname'].split('.')[1]
        date_fixed = date_orig + pd.Timedelta(hours=delay_hours)
        fname_fixed = fname_orig['sensor_name']+'_'+date_fixed.strftime('%Y%m%d_%H%M%S')+fname_ext
        if verbose:
            print(f'Renaming file: {os.path.basename(fname)} > {fname_fixed}')
        
        # rename file
        os.rename(src=fname, dst=os.path.join(os.path.dirname(fname), fname_fixed))

#%%
# ------------------------
# Audio Metadata Functions
# ------------------------

def print_damaged_files(df):
    for _, row in df.iterrows():
        try:
            util.audio_header(row.path_audio)
        except:
            print(row.fname)

def get_audio_metadata(path_dir, path_save, dropna=True, verbose=False) -> None:
    """
    Extracts audio metadata from files in a directory and saves it to a CSV file.

    Args:
        path_dir (str): The directory containing audio files.
        path_save (str): The path where the metadata CSV file will be saved.
        dropna (bool, optional): If True, remove rows with missing values (default: True).
        verbose (bool, optional): If True, display progress and information (default: False).

    Returns:
        None

    Note:
        This function extracts metadata from audio files in the specified directory using the 'util.get_metadata_dir' function.
        It adds a 'site' column based on the file names, drops rows with missing values if 'dropna' is True,
        and saves the resulting DataFrame to a CSV file at 'path_save'.
    """
    df = util.get_metadata_dir(path_dir, verbose=verbose)
    df['site'] = df.fname.str.split('_').str[0]  # include site column
    if dropna:
        df.dropna(inplace=True)  # remove problematic files
    # save dataframes to csv
    df.to_csv(path_save, index=False)

def random_sample_metadata(df, n_samples_per_site=10, hour_sel=None, random_state=None):
    """ Get a random sample form metadata DataFrame """
    if hour_sel==None:
        hour_sel = [str(i).zfill(2) for i in range(24)]

    # format data
    df.loc[:,'hour'] = df.loc[:,'date'].str[11:13].astype(str)
    sensor_list = df.sensor_name.unique()

    # Batch process
    df_out = pd.DataFrame()
    for sensor_name in sensor_list:
        df_sel = df.loc[(df.sensor_name==sensor_name) & (df.hour.isin(hour_sel)),:]
        df_sel = df_sel.sample(n_samples_per_site, random_state=random_state)
        df_out = pd.concat([df_out, df_sel])

    df_out.reset_index(drop=True, inplace=True)

    return df_out

def metadata_summary(df):
    """ Get a summary of a metadata dataframe of the acoustic sampling

    Parameters
    ----------
    df : pandas DataFrame or string with path to a csv file
        The dataframe must have the columns site, date, sample_length.
        Use maad.util.get_audio_metadata to compile the dataframe.

    Returns
    -------
    pandas DataFrame
        A summary of each site
    """
    # Function argument validation
    df = input_validation_df(df)
        
    df['date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df_summary = {}
    for site, df_site in df.groupby('site'):
        site_summary = {
            'date_ini': str(df_site.date_fmt.min()),
            'date_end': str(df_site.date_fmt.max()),
            'n_recordings': len(df_site),
            'duration': str(df_site.date_fmt.max() - df_site.date_fmt.min()),
            'sample_length': df_site.length.mean().round(),
            'time_diff': df_site['date_fmt'].sort_values().diff().median(),
        }
        df_summary[site] = site_summary
    df_summary = pd.DataFrame(df_summary).T
    return df_summary.reset_index().rename(columns={'index': 'site'})

#%%
# --------------------
# Time Lapse Functions
# --------------------
def concat_audio(flist, sample_len=1, verbose=False, display=False):
    """ Concatenates samples using a list of audio files

    Parameters
    ----------
    flist : list or pandas Series
        List of files to concatenate
    sample_len : float, optional
        Length in seconds of each sample, default is 1 second
    display : bool, optional
        If true displays the audio spectrogram, by default False
    
    Return
    ------
    """
    
    # Compute long wav
    long_wav = list()
    for idx, fname in enumerate(flist):
        if verbose:
            print(fname)
        s, fs = sound.load(fname)
        s = sound.trim(s, fs, 0, sample_len)
        long_wav.append(s)

    long_wav = np.concatenate(long_wav)
    
    # Plot
    if display:
        Sxx, tn, fn, ext = sound.spectrogram(
            long_wav, fs, window='hann', nperseg=1024, noverlap=512)
        fig, ax = plt.subplots(1,1, figsize=(10,3))
        util.plot_spectrogram(Sxx, extent=[0, 24, 0, 11],
                            ax=ax, db_range=80, gain=25, colorbar=False)
        ax.set_xlabel('Time [Hours]')
        ax.set_xticks(range(0,25,4))

    return long_wav, fs

def audio_timelapse(
        sample_len, sample_period='30T', date_range=None, path_save=None, save_audio=True, save_spectrogram=True, verbose=True)  -> None:
    """ Build audio timelapse """
    
    # Function argument validation
    df = input_validation_df(df)
    date_range = pd.to_datetime(date_range)

    # select files to create timelapse
    df.date = pd.to_datetime(df.date)
    idx_dates = df.date.between(date_range[0], date_range[1], inclusive='left')
    df_timelapse = df.loc[idx_dates,:]
    df_timelapse.set_index('date', inplace=True)
    df_timelapse['day'] = df_timelapse.date.dt.date
    ngroups = df_timelapse.groupby(['site', 'day']).ngroups

    # create time lapse
    print(f'Processing {ngroups} groups:')
    for site, df_site in df_timelapse.groupby('site'):
        print(site)
        df_site.sort_values('date_fmt', inplace=True)
        df_site = df_site.resample(sample_period).first()
        long_wav, fs = concat_audio(df_site['path_audio'],
                                    sample_len=sample_len, 
                                    verbose=verbose)
        if save_audio:
            sound.write(f'{path_save}{site}_timelapse.wav', fs, long_wav, bit_depth=16)
        
        if save_spectrogram:
            print('under construction')

#%%
# ----------------
# Main Entry Point
# ----------------
def main():
    parser = argparse.ArgumentParser(
        description="Perform preprocessing operations on audio data.")
    parser.add_argument(
        "operation", 
        choices=["get_audio_metadata", 
                 "metadata_summary",
                 "plot_sensor_deployment",
                 "audio_timelapse",
                 "add_file_prefix"], 
        help="Preprocessing operation")
    
    parser.add_argument("--path", type=str, help="Path to directory to search")
    parser.add_argument("--path_save", type=str, help="Path and filename to save results")
    parser.add_argument("--dropna", action="store_true", help="Drop NAN values from metadata")
    parser.add_argument("--length", type=float, help="Sample length for audio timelapse")
    parser.add_argument("--recursive", "-r", action="store_true", help="Enable recursive mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()

    if args.operation == "get_audio_metadata":
        result = get_audio_metadata(args.path, args.path_save, args.dropna, args.verbose)
    elif args.operation == "add_file_prefix":
        result = add_file_prefix(args.path, args.recursive, args.verbose)
    elif args.operation == "plot_sensor_deployment":
        result = plot_sensor_deployment(args.path)
    elif args.operation == "audio_timelapse":
        result = audio_timelapse(args.path, args.length, args.path_save)
    elif args.operation == "metadata_summary":
        result = metadata_summary(args.path)

    print("Result:", result)

if __name__ == "__main__":
    main()
