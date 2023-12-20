"""
Graphical soundscape with local maxima
WARNING: THIS SCRIPT IS UNDER CONSTRUCTION

"""
import pandas as pd
import yaml
from maad import sound, util
from maad.rois import spectrogram_local_max
from maad.features import graphical_soundscape, plot_graph
import matplotlib.pyplot as plt

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

path_audio = config["input_data"]["path_audio"]
path_metadata = config["preprocessing"]["path_save_metadata_full"]
path_save = config["graph_soundscapes"]["path_save_gs"]
target_fs = config["graph_soundscapes"]["target_fs"]
nperseg = config["graph_soundscapes"]["nperseg"]
noverlap = config["graph_soundscapes"]["noverlap"]
db_range = config["graph_soundscapes"]["db_range"]
min_distance = config["graph_soundscapes"]["min_distance"]
threshold_abs = config["graph_soundscapes"]["threshold_abs"]

#%% Test output on a single file
fname = '/Volumes/lacie_exfat/Downloads/H79_sample/H79_20230501_235500.WAV'
s, fs = sound.load(fname)
Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
Sxx_db = util.power2dB(Sxx, db_range=db_range)

peaks = spectrogram_local_max(
    Sxx_db, tn, fn, ext,
    min_distance,
    threshold_abs,
    display=True,
)

#%% Compute graphical soundscape per site

df = pd.read_csv(path_metadata, dtype={'time': 'str'})
for site, df_site in df.groupby('site'):
    graph = graphical_soundscape(
        df_site.reset_index(drop=True),
        threshold_abs,
        target_fs=target_fs,
        nperseg=nperseg,
        noverlap=noverlap,
        db_range=db_range,
        min_distance=min_distance)
    
    graph.to_csv(f'{path_save}{site}_graph.csv')
    plot_graph(graph, savefig=True, fname=f'{path_save}{site}_graph.png')
