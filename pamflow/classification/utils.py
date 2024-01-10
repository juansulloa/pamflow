#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary files to help in the detection of soundmarks
"""
import glob
import pandas as pd
import numpy as np
import os
import warnings
from maad import sound, util

#%% Custom functions

# Load annotations
def merge_mannot_files(path_annot, verbose=False):
    """ Batch load manual annotations """
    if isinstance(path_annot, str):
        flist = glob.glob(path_annot+'*.txt')
    elif isinstance(path_annot, list):
        flist = path_annot
    else:
        warnings.warn("Input parameter should be of type str or list.", UserWarning)

    if verbose:
        print('Number of files found:', len(flist))

    df_annot = pd.DataFrame()
    for fname in flist:
        aux = pd.read_csv(fname, sep='\t')
        aux['File Name'] = os.path.basename(fname)
        df_annot = pd.concat([df_annot, aux], axis=0)
    
    return df_annot

def match_files(path_annot, path_audio):
    """ Match annotations and audio files """
    flist_annot = glob.glob(path_annot+'*.txt')
    flist_audio = glob.glob(path_audio+'*.[wW][aA][vV]')

    # Get basename for annotation file
    flist_annot_base = [os.path.basename(file) for file in flist_annot]
    flist_annot_base = [file.split('.')[0] for file in flist_annot_base]
    flist_audio_base = [os.path.basename(file) for file in flist_audio]
    flist_audio_base = [file.split('.')[0] for file in flist_audio_base]

    # Create a annotation DataFrame
    df_annot = pd.DataFrame({'fpath_annot': flist_annot,
                            'basename': flist_annot_base})

    df_audio = pd.DataFrame({'fpath_audio': flist_audio,
                            'basename': flist_audio_base})

    df_match = df_audio.merge(df_annot, on='basename')
    df_match.set_index('basename', inplace=True)
    return df_match

def build_annotated_audio_track(data, path_audio, min_t, max_t, silence_len=0.1,
                                path_save=None):
    """ Build a track for fast annotation """
    # initialize audio track and annotation track
    seg_audio = np.zeros([0])
    seg_annot = pd.DataFrame({'min_t': [0], 'max_t': [0], 'label': ['0']})

    # iterate through data
    for idx, (_, row) in enumerate(data.iterrows()):
        # load data
        s, fs = sound.load(row[path_audio])
        silence = np.zeros(int(silence_len*fs))
        # transform audio
        s_trim = sound.trim(s, fs, min_t=row[min_t], max_t=row[max_t])
        # concat audio
        seg_audio = np.concatenate([seg_audio, silence, s_trim])    
        # add annotation to dataframe
        seg_length = row[max_t] - row[min_t] + silence_len
        annot = pd.DataFrame({'min_t': [seg_annot.loc[idx, 'max_t'] + silence_len],
                            'max_t': [seg_annot.loc[idx, 'max_t'] + seg_length],
                            'label': [row[label]]},
                            index = [idx + 1])
                            
        seg_annot = pd.concat([seg_annot, annot], axis=0)

    seg_annot.drop(index=0, inplace=True)

    # Save data
    # If save_location is not provided, use the current working directory
    if path_save is None:
        path_save = os.getcwd()

    if not os.path.exists(path_save):
        os.makedirs(path_save)

    util.write_audacity_annot(os.path.join(path_save, 'annot.txt'), seg_annot)
    sound.write(os.path.join(path_save, 'audio.wav'), fs, seg_audio, bit_depth=16)
    print(f"Audio and annotation saved at: {path_save}")

#%% VARIABLES
path_annot = '/Users/jsulloa/Downloads/annot/'
path_audio = '/Users/jsulloa/Downloads/audio/'
n_segments = 10 # number of segments per category
labels = ['blcjay1']  # list, labels that are neeeded to annotate
min_conf = 0.5

# build annotated_audio_track
silence_len = 0.1
path_audio = 'Path Audio'
min_t = 'Begin Time (s)'
max_t = 'End Time (s)'
label = 'Species Code'
path_save = '/Users/jsulloa/Downloads/output/'

#%% Main
# load data
matched_files = match_files(path_annot, path_audio)
df_annot = merge_mannot_files(matched_files.fpath_annot.to_list(), verbose=False)

# filter dataframe
df_annot = df_annot.loc[
    (df_annot['Confidence']>min_conf) & (df_annot['Species Code'].isin(labels))]

# add path audio column
df_annot['Path Audio'] = matched_files.loc[
    df_annot['File Name'].str.split('.').str[0].values,'fpath_audio'].values

# segments
build_annotated_audio_track(df_annot, path_audio, min_t, max_t, silence_len, path_save)
df_annot.to_csv(os.path.join(path_save, 'df_annot.csv'))
