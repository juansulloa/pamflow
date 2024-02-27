import pandas as pd
import glob
from utils import merge_annot_files

# Load data a format it as an abundance matrix with files rows
path_annot = '../../../output/birdnet/detections/'

flist = glob.glob(f"{path_annot}/**/*.csv", recursive=True)
df = merge_annot_files(flist, rtype='csv')
df['Confidence'] = (df['Confidence'] >= 0.8).astype(int)
df_clean = df.loc[df.Confidence==1]

# Pivot table to get the desired structure
pivot_table = pd.pivot_table(
    df_clean, index='Fname', columns='Scientific name', 
    values='Confidence', aggfunc='sum', fill_value=0)

#pivot_table.reset_index(inplace=True)
pivot_table.to_csv('../../../output/birdnet/birdnet_species_matrix_minconf0.8.csv')

# Format the table per site
t1_plot_id = pd.read_csv('../../../input/t1_plot_id.csv')

pivot_table['sensor_name'] = pivot_table.index.str.split('_').str[0].values
pivot_table_site = pivot_table.groupby('sensor_name').sum()
pivot_table_site = t1_plot_id.merge(pivot_table_site, on='sensor_name')

pivot_table_site.to_csv('../../../output/birdnet/birdnet_site-species_matrix_minconf0.8.csv', index=False)