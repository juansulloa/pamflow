""" Utilities to compute graphical soundscapes from audio files 

The functions here are a variant of the original graphical soundscapes introduced by Campos-Cerqueira et al. The peaks are detected on the spectrogram instead of detecting peaks on the spectrum. Results are similar but not equal to the ones computed using seewave in R.

References:
  - Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
  - Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
  - Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
"""
import os
import yaml
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from maad import sound, util
from maad.rois import spectrogram_local_max
from maad.features import graphical_soundscape, plot_graph

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
# ----------------
# Main Entry Point
# ----------------
def main():
    parser = argparse.ArgumentParser(
        description="Compute graphical soundscape on audio data.")
    parser.add_argument(
        "operation", 
        choices=[
            "spectrogram_local_max",
            "graphical_soundscape",
            "plot_graph",
        ],
        help="Graphical soundscape operation")
    
    parser.add_argument("--path", type=str, help="Path to directory with audio files")
    parser.add_argument("--path_save", type=str, help="Path and filename to save results")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--display", "-d", action="store_true", help="Enable to display plot")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()
    
    # Load configuration
    config_file = args.config
    config = load_config(config_file)
    target_fs = config["graph_soundscapes"]["target_fs"]
    nperseg = config["graph_soundscapes"]["nperseg"]
    noverlap = config["graph_soundscapes"]["noverlap"]
    db_range = config["graph_soundscapes"]["db_range"]
    min_distance = config["graph_soundscapes"]["min_distance"]
    threshold_abs = config["graph_soundscapes"]["threshold_abs"]

    if args.operation == "spectrogram_local_max":
        s, fs = sound.load(args.path)
        s = sound.resample(s, fs, target_fs, res_type="scipy_poly")
        Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
        Sxx_db = util.power2dB(Sxx, db_range=db_range)
        result = spectrogram_local_max(Sxx_db, tn, fn, ext, min_distance, 
                                       threshold_abs, display=args.display)
        print(result)

    elif args.operation == "graphical_soundscape":
        graph = graphical_soundscape(
            args.path,
            threshold_abs,
            target_fs=target_fs,
            nperseg=nperseg,
            noverlap=noverlap,
            db_range=db_range,
            min_distance=min_distance)
        
        graph.to_csv(args.path_save)
        
        if args.display:
            plot_graph(graph)

if __name__ == "__main__":
    main()
