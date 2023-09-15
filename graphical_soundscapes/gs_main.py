"""
Graphical soundscape with local maxima
WARNING: THIS SCRIPT IS UNDER CONSTRUCTION

"""
import pandas as pd
import yaml
from maad import sound, util
from gs_utils import spectrogram_local_max, graphical_soundscape, plot_graph
import matplotlib.pyplot as plt

#%% Load configuration files
# Open the config file and load its contents into a dictionary
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

path_audio = config["input_data"]["path_audio"]
path_metadata = config["preprocessing"]["path_save_metadata_clean"]
target_fs = 48000
nperseg = 256
noverlap = 128
db_range = 80
min_distance = 1
threshold_abs = -50

#%%
df = pd.read_csv(path_metadata)

for site, df_site in df.groupby('site'):
    graph = graphical_soundscape(
        df_site.reset_index(drop=True),
        target_fs,
        nperseg,
        noverlap,
        db_range,
        min_distance,
        threshold_abs
    )
    plot_graph(graph)

#%%
fname = "/Users/jsulloa/Dropbox/PostDoc/iavh/2020_Putumayo/putumayo_soundmarks/audio_examples/RUG03_20190805_183000.wav"
s, fs = sound.load(fname)
Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
Sxx_db = util.power2dB(Sxx, db_range=db_range)

peaks = spectrogram_local_max(
    Sxx_db, tn, fn, ext,
    min_distance,
    threshold_abs,
    display=True,
)


peaks = spectrogram_local_max(
    Sxx_db, tn, fn, ext,
    min_distance=1,
    threshold_abs=None,
    #footprint=np.ones([50,50]),
    display=True,
)