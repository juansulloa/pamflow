import pandas as pd
from maad import util
from preprocessing_utils import (add_file_prefix, 
                                 metadata_summary,
                                 plot_sensor_deployment,
                                 random_sample_metadata)

# Set variables
folder_name = '/Volumes/lacie_exfat/Cataruben/audio/'
path_save_metadata_full = '/Volumes/lacie_exfat/Cataruben/metadata/metadata_full.csv'
path_save_metadata_clean = '/Volumes/lacie_exfat/Cataruben/metadata/metadata_clean.csv'
path_save_metadata_sample = '/Volumes/lacie_exfat/Cataruben/metadata/metadata_sample.csv'

#%% 1. Add file prefix according to file names
add_file_prefix(folder_name, recursive=True)

#%% 2. Get audio metadata
df_full = util.get_metadata_dir(folder_name, verbose=True)
df_full['site'] = df_full.fname.str.split('_').str[0]  # include site column
df_full = df_full.loc[~df_full.sample_rate.isna(),:]  # remove nan values
df_full.loc[:,'date_fmt'] = pd.to_datetime(df_full.date,  format='%Y-%m-%d %H:%M:%S')

# Check dataframe consistency
metadata_summary(df_full)

# sites ['CAT003', 'CAT005', 'CAT006', 'CAT012'] have bad configuration and must be removed
rm_sites = ['CAT003', 'CAT005', 'CAT006', 'CAT012']
df = df_full.loc[~df_full.site.isin(rm_sites),]
plot_sensor_deployment(df)

# save dataframes to csv
df_full.to_csv(path_save_metadata_full, index=False)
df.to_csv(path_save_metadata_clean, index=False)

#%% 3. Sample audio for manual analisys
# Conduct a random sampling of 6 recordings in a directory associated with a sampling point. Sampling is restricted to each peak of acoustic activity at dawn (05h-08h) and dusk (17h-20h) to identify vocalizations of birds and amphibians, and record the presence or absence of anthropophony, biophony, and geophony

peak_hours = ['05', '06', '07', '08', '17', '18', '19', '20']
df_sample = random_sample_metadata(
    df, n_samples_per_site=12, hour_sel=peak_hours, random_state=123)
df_sample.to_csv(path_save_metadata_sample, index=False)
