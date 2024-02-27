#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import os
import argparse
import matplotlib.pyplot as plt
import pandas as pd
from maad import sound, util
from pamflow.preprocess.utils import find_files, plot_sensor_deployment
from maad.features import plot_graph
import yaml

def load_config(file_path):
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

def plot_spectrogram(input, output, config):
    # load configuration
    config = load_config(config)
    nperseg = config['plot']['nperseg']
    noverlap = config['plot']['noverlap']
    fig_height = config['plot']['fig_height']
    fig_width = config['plot']['fig_width']
    db_range = config['plot']['db_range']
    cmap = config['plot']['colormap']
    # plot spectrogram
    s, fs = sound.load(input)
    Sxx, _, _, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
    ext[2], ext[3] = ext[2]/1000, ext[3]/1000
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    util.plot_spectrogram(Sxx, ext, db_range=db_range, ax=ax, colorbar=False, cmap=cmap)
    ax.set_ylabel('Frequency (kHz)')
    ax.set_xlabel('Time (s)')
    fname_save = str(fname)[:-4] + '.png'
    plt.savefig(fname_save)
    plt.close(fig)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform preprocessing operations on audio data.")
    parser.add_argument(
        "operation", 
        choices=[
            "spectrogram",
            "sensor_deployment",
            "plot_graph",
        ],
        help="Plot operation")
    
    parser.add_argument("--input", "-i", 
                        type=str, help="Path to directory to search")
    parser.add_argument("--output", "-o", 
                        type=str, help="Path and filename to save results")
    parser.add_argument("--config", "-c", type=str, default='config.yaml',
                        help="Path to configuration file. ")
    parser.add_argument("--recursive", "-r", 
                        action="store_true", help="Enable recursive mode")
    args = parser.parse_args()

    if args.operation == "spectrogram":
        if os.path.isdir(args.input):
            flist = find_files(args.input, endswith='.wav')
        else:
            flist = [args.input]
        
        for fname in flist:
            plot_spectrogram(fname, args.output, args.config)
    
    elif args.operation == "sensor_deployment":
        _ = plot_sensor_deployment(args.input)

    elif args.operation == "plot_graph":
        if os.path.isdir(args.input):
            flist = find_files(args.input, endswith='.csv')
        else:
            flist = [args.input]
        
        for fname in flist:
            graph = pd.read_csv(fname, index_col=0)
            fig, ax = plt.subplots()
            plot_graph(graph)
            fname_save = str(fname)[:-4] + '.png'
            plt.savefig(fname_save)
            plt.close(fig)
            