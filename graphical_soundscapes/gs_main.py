"""
Graphical soundscape with local maxima
WARNING: THIS SCRIPT IS UNDER CONSTRUCTION

"""
#%% Load libraries
import yaml
import os
import pandas as pd
from maad import sound
from gs_utils import spectrogram_local_max, graphical_soundscape, plot_graph
import matplotlib.pyplot as plt

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

path_audio = config["input_data"]["path_audio"]
path_metadata = config["preprocessing"]["path_save_metadata_t2"]
#path_save_gs = config["graph_soundscapes"]["path_save_gs"]  # location to save the dataframe
path_save_gs = '../../output/dataframes_gs/python_gs/'
path_save_fig = config["graph_soundscapes"]["path_save_fig"]
target_fs = 48000
nperseg = 256
noverlap = 128
db_range = 80
min_peak_distance = 5
min_peak_amplitude = 30
df = pd.read_csv(path_metadata)

#%% Test parameters on random files to validate parameters
s, fs = sound.load(
    df.path_audio.sample(1).iloc[0]
)
s = sound.resample(s, fs, target_fs=target_fs, res_type='scipy_poly')
fpeaks = spectrogram_local_max(
    s,
    target_fs,
    nperseg,
    noverlap,
    db_range,
    min_peak_distance,
    min_peak_amplitude,
    display=True,
)
#%% Batch compute graphical soundscape per sampling site  
for site, df_site in df.groupby('site'):
    graph = graphical_soundscape(
        df_site.reset_index(drop=True),
        target_fs,
        nperseg,
        noverlap,
        db_range,
        min_peak_distance,  
        min_peak_amplitude
    )
    graph.to_csv(os.path.join(path_save_gs, 't2_'+site+'_py.csv'))
    plot_graph(graph, savefig=True, fname=os.path.join(path_save_gs, 't2_'+site+'_py.png'))
