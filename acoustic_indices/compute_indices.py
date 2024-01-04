""" Utility functions to compute acoustic indices """

import os
import argparse
import yaml
import concurrent.futures
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from maad import sound, features, util

#%% Load configuration file
def load_config(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

#%% Function argument validation
def input_validation(data_input):
    """ Validate dataframe or path input argument """
    if isinstance(data_input, pd.DataFrame):
        df = data_input
    elif isinstance(data_input, str):
        if os.path.isdir(data_input):
            print('Collecting metadata from directory path')
            df = util.get_metadata_dir(data_input)
            print(f'Done! {df.shape[0]} files found')
        elif os.path.isfile(data_input) and data_input.lower().endswith(".csv"):
            print('Loading metadata from csv file')
            try:
                # Attempt to read all wav data from the provided file path.
                df = pd.read_csv(data_input) 
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {data_input}")
    else:
        raise ValueError("Input 'data' must be either a Pandas DataFrame, a file path string, or None.")
    return df

#%%
def compute_acoustic_indices(s, Sxx, tn, fn):
    """
    Parameters
    ----------
    s : 1d numpy array
        acoustic data
    Sxx : 2d numpy array of floats
        Amplitude spectrogram computed with maad.sound.spectrogram mode='amplitude'
    tn : 1d ndarray of floats
        time vector with temporal indices of spectrogram.
    fn : 1d ndarray of floats
        frequency vector with temporal indices of spectrogram..

    Returns
    -------
    df_indices : pd.DataFrame
        Acoustic indices
    """
    
    # Set spectro as power (PSD) and dB scales.
    Sxx_power = Sxx**2
    Sxx_dB = util.amplitude2dB(Sxx)

    # Compute acoustic indices
    ADI = features.acoustic_diversity_index(
        Sxx, fn, fmin=0, fmax=24000, bin_step=1000, index='shannon', dB_threshold=-40)
    _, _, ACI = features.acoustic_complexity_index(Sxx)
    NDSI, xBA, xA, xB = features.soundscape_index(
        Sxx_power, fn, flim_bioPh=(2000, 20000), flim_antroPh=(0, 2000))
    Ht = features.temporal_entropy(s)
    Hf, _ = features.frequency_entropy(Sxx_power)
    H = Hf * Ht
    BI = features.bioacoustics_index(Sxx, fn, flim=(2000, 11000))
    NP = features.number_of_peaks(Sxx_power, fn, mode='linear', min_peak_val=0, 
                                  min_freq_dist=100, slopes=None, prominence=1e-6)
    SC, _, _ = features.spectral_cover(Sxx_dB, fn, dB_threshold=-70, flim_LF=(1000,20000))
    
    # Structure data into a pandas series
    df_indices = pd.Series({
        'ADI': ADI,
        'ACI': ACI,
        'NDSI': NDSI,
        'BI': BI,
        'Hf': Hf,
        'Ht': Ht,
        'H': H,
        'SC': SC,
        'NP': int(NP)})

    return df_indices

#%%
def compute_acoustic_indices_single_file(path_audio, target_fs=48000, verbose=True):
    if verbose:
        print(f'Processing file {path_audio}', end='\r')

    # load audio
    s, fs = sound.load(path_audio)    
    s = sound.resample(s, fs, target_fs, res_type='scipy_poly')

    # Compute the amplitude spectrogram and acoustic indices
    Sxx, tn, fn, _ = sound.spectrogram(
        s, fs, nperseg = 1024, noverlap=0, mode='amplitude')
    df_indices_file = compute_acoustic_indices(s, Sxx, tn, fn)
    
    return df_indices_file

#%%
def batch_compute_acoustic_indices(data, path_save=None):
    df = input_validation(data)
    sensor_list = df.sensor_name.unique()
    
    # Loop through sites
    for sensor_name in sensor_list:
        flist_sel = df.loc[df.sensor_name==sensor_name,:]
        
        df_indices = pd.DataFrame()
        for idx_row, row in flist_sel.iterrows():
            print(f'{idx_row+1} / {flist_sel.index[-1]}: {row.fname}', end='\r')
            # Load and resample to 48 kHz
            df_indices_file = compute_acoustic_indices_single_file(row.path_audio)
                
            # add file information to dataframes
            add_info = row[['fname', 'sensor_name', 'date']]
            df_indices_file = pd.concat([add_info, df_indices_file])
            
            # append to dataframe
            df_indices = pd.concat([df_indices, df_indices_file.to_frame().T])
            
        # Save dataframes
        df_indices.to_csv(path_save+sensor_name+'_indices.csv', index=False)

#%% Parellel computing
def compute_indices_parallel(data, target_fs=48000, n_jobs=4):
    df = input_validation(data)
    if n_jobs == -1:
        n_jobs = os.cpu_count()

    print(f'Computing acoustic indices for {df.shape[0]} files with {n_jobs} threads')
    
    # Use concurrent.futures for parelell execution
    files = df.path_audio.to_list()
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        # Use submit for each task
        futures = {executor.submit(compute_acoustic_indices_single_file, file, target_fs): file for file in files}

        # Get results when tasks are completed
        results = []
        for future in concurrent.futures.as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                result['fname'] = os.path.basename(file_path)
                results.append(result)
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Build dataframe with results
    df_out = pd.DataFrame(results)
    return df_out

#%% Sequential computing
def compute_indices_sequential(data, target_fs):
    df = input_validation(data)
    print(f'Computing acoustic indices for {df.shape[0]} files')
    
    files = df.path_audio.to_list()
    results = []
    for i, file_path in enumerate(files, start=1):
        result = compute_acoustic_indices_single_file(file_path, target_fs)
        result['fname'] = os.path.basename(file_path)
        results.append(result)
    
    # Build dataframe with results
    df_out = pd.DataFrame(results)
    return df_out

def compute_indices(data, target_fs, n_jobs):
    if n_jobs == 1:
        df_out = compute_indices_sequential(data, target_fs)
    else:
        df_out = compute_indices_parallel(data, target_fs, n_jobs)
    return df_out

#%% 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Compute acoustic indices on audio data")
    parser.add_argument("--input", "-i", type=str, 
                    help="Path to metadata or directory with audio files. "
                         "If providing a directory, all audio files in the directory will be processed.")
    parser.add_argument("--output", "-o", type=str,
                    help="Path and filename to save results. "
                         "Results will be saved to a file with the specified name at the specified location.")
    parser.add_argument("--config", "-c", type=str,
                    help="Path to config file. "
                         "The config file should contain all additional settings for your script.")
    parser.add_argument( "--sites", "-s", nargs="+", default=None,
                    help="Specify sites to execute the operation (default: None)")
    args = parser.parse_args()

    # Load configuration
    df = input_validation(args.input)
    config_file = args.config
    config = load_config(config_file)
    target_fs = config["acoustic_indices"]["target_fs"]
    n_jobs = config["acoustic_indices"]["n_jobs"]
    group_by_site = config["acoustic_indices"]["group_by_site"]
    select_sites = args.sites

    # If file list provided filter dataframe
    if select_sites is None:
        n_sites = df.groupby('sensor_name').ngroups
        site_list = df.sensor_name.unique()
    else:
        df = df[df['sensor_name'].isin(select_sites)]
        n_sites = df.groupby('sensor_name').ngroups
        site_list = df.sensor_name.unique()
    print(f'Computing indices over {n_sites} sites: {site_list}')

    # Format output per site or per batch
    if group_by_site:  
        for site, df_site in df.groupby('sensor_name'):
            df_out = compute_indices(df_site, target_fs, n_jobs)
            fname_save = os.path.join(args.output, f'{site}_indices.csv')
            df_out.to_csv(fname_save, index=False)
            print(f'{site} Done! Results are stored at {fname_save}')

    else:
        df_out = compute_indices(df, target_fs, n_jobs)
        df_out.to_csv(args.output, index=False)
        print(f'Done! Results are stored at {args.output}')
