"""
POSTPROCESS BIRDNET DETECTIONS

1. Merge all annotations into a single file
2. Select only the species of interest
3. Plot daily activity
4. Plot proportion of activity
"""
#%% Load packages and variables
import glob
import pandas as pd
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

site_dist_dict = {
    'P1': 600, 'P2': 500, 'P3': 400, 'P4': 300, 'P5': 200, 'P6': 100,
    'Z1': 600, 'Z2': 500, 'Z3': 400, 'Z4': 300, 'Z5': 200, 'Z6': 100}

plt_colors = {'t0': '#2b8cbe',
              't1': '#7bccc4',
              't2': '#ccebc5',
              'P': '#f1a340',
              'Z': '#998ec3',
              'Pozo': '#f1a340',
              'Control': '#998ec3',
              'P6-t0': '#2b8cbe',
              'P6-t2': '#ccebc5',}

"""  
# Load all detections and save to file -- Do it once
path_detections = '../../output/detections/bats_32k/'
path_save = '../../output/detections/bats_32k_detections_compiled.csv'
flist = glob.glob(path_detections+'*.txt')
print('Number of files found:', len(flist))

df_annot = pd.DataFrame()
for fname in flist:
    aux = pd.read_csv(fname, sep='\t')
    aux['fname'] = os.path.basename(fname).replace('.BirdNET.selection.table.txt', '.WAV')
    df_annot = pd.concat([df_annot, aux], axis=0)

df_annot.to_csv(path_save, index=False)
"""
#%% Set variables
path_detections_compiled = '../../output/detections/bats_32k_detections_compiled.csv'
#path_detections_compiled = '../../output/detections/custom_detections_compiled.csv'
#path_detections_compiled = '../../output/detections/birdnet_detections_compiled.csv'
path_metadata = '../../output/metadata/metadata_t0-t1-t2.csv'
sp_focal = 'MOLMOL'  # ['ENGPUS', 'peptyr1', 'grekis', 'MYO01', 'SACBIL', 'MOLMOL']
birdnet_confidence_th = 0.7

#%% LOAD AND PREPARE DATA
df_metadata = pd.read_csv(path_metadata)
df_annot = pd.read_csv(path_detections_compiled)

# select columns
df = df_annot[['Species Code', 'Confidence', 'fname']]
# select species
df = df.loc[df_annot['Species Code'] == sp_focal,:]
# filter by confidence
df['counts'] = (df.Confidence>=birdnet_confidence_th).astype(int)
df = df[['fname', 'counts']].groupby('fname').sum()
df.reset_index(inplace=True)

# merge with metadata
df = df.merge(df_metadata[['fname', 'site', 'day', 'hour', 'period']], 
              on='fname', how='outer')
df['counts'].fillna(0, inplace=True)
df['site'] = df['site'].str[0:2]
df['treatment'] = df['site'].str[0]
# counts to seconds
if sp_focal in ['MOLMOL', 'MYO01', 'SACBIL']:
    df['counts'] = df['counts'] * 0.5 # for bats at 32 kHz 3s*32k/192k
else:
    df['counts'] = df['counts'] / 3

#%% COMPUTE AND PLOT ACOUSTIC ACTIVITY
df_acoustic_activity = df[
    ['site', 'day', 'period', 'counts']].groupby(['site', 'day', 'period']).sum()
df_acoustic_activity.reset_index(inplace=True)
df_acoustic_activity.rename(
    columns={'counts': 'acoustic_activity', 'period': 'periodo'}, inplace=True)
df_acoustic_activity['dist'] = df_acoustic_activity['site'].replace(site_dist_dict)
df_acoustic_activity['treatment'] = df_acoustic_activity['site'].str[0]
df_acoustic_activity.to_csv(f'../../output/detections/{sp_focal}_acoustic_activity.csv', index=False)

# Plot
idx_dist = df_acoustic_activity.dist.isin([100, 200, 500])
idx_t0 = df_acoustic_activity.periodo=='t0'
idx_t2 = df_acoustic_activity.periodo=='t2'
plt_data_t0 = df_acoustic_activity.loc[idx_dist & idx_t0]
plt_data_t2 = df_acoustic_activity.loc[idx_dist & idx_t2]
n_detections_t0 = plt_data_t0.acoustic_activity.sum().astype(int)
n_detections_t2 = plt_data_t2.acoustic_activity.sum().astype(int)

fig, ax = plt.subplots(1,2, figsize=(10,5), sharey=True)
sns.boxplot(plt_data_t0, x='dist', y='acoustic_activity', 
            hue='treatment', palette=plt_colors, linewidth=0.75, ax=ax[0])
ax[0].set_xlabel('Distancia')
ax[0].set_ylabel('Actividad acústica')
ax[0].set_title(f'{sp_focal} - t0 - {n_detections_t0} detecciones')

sns.boxplot(plt_data_t2, x='dist', y='acoustic_activity', 
            hue='treatment', palette=plt_colors, linewidth=0.75, ax=ax[1])
ax[1].set_xlabel('Distancia')
ax[1].set_ylabel('Actividad acústica')
ax[1].set_title(f'{sp_focal} - t2 - {n_detections_t2} detecciones')
sns.despine(trim=True)
fig.tight_layout()
plt.savefig(f'../../output/figures/detections/acoustic_activity_boxplot_{sp_focal}.png')

#%% COMPUTE AND PLOT TEMPORAL ACTIVITY
df_temporal = df[
    ['hour', 'counts', 'treatment', 'period']].groupby(['hour', 'treatment', 'period']).sum()
df_temporal.reset_index(inplace=True)

df_out = pd.DataFrame()
for name, group in df_temporal.groupby(['period', 'treatment']):
    aux = group[['counts', 'hour']].groupby('hour').sum()
    aux.reset_index(inplace=True)
    aux['counts'] = aux.counts/aux.counts.sum()
    aux['period'] = name[0]
    aux['treatment'] = name[1]
    df_out = pd.concat([df_out, aux])
df_out.to_csv(f'../../output/detections/{sp_focal}_temporal_activity.csv', index=False)

# Plot normalized histogram
fig, ax = plt.subplots(1,2, figsize=(10,5), sharey=True)
for idx, periodo in enumerate(['t0', 't2']):
    sns.barplot(df_out.groupby(['period', 'treatment']).get_group((periodo, 'P')), 
                x='hour', y='counts', color=plt_colors['P'], alpha=0.6, ax=ax[idx], width=1)
    sns.barplot(df_out.groupby(['period', 'treatment']).get_group((periodo, 'Z')), 
                x='hour', y='counts', color=plt_colors['Z'], alpha=0.6, ax=ax[idx], width=1)
    ax[idx].set_xlabel('Hora')
    ax[idx].set_ylabel('Actividad acústica normalizada')
    ax[idx].set_title(f'Especie: {sp_focal} - periodo: {periodo}')
    sns.despine(trim=True)

fig.tight_layout()
plt.savefig(f'../../output/figures/detections/temporal_activity_hist_{sp_focal}.png')

# Plot kde
fig, ax = plt.subplots(1,2, figsize=(10,5), sharey=True)
for idx, periodo in enumerate(['t0', 't2']):
    df_P = df.loc[df.period==periodo].groupby('treatment').get_group('P')
    df_Z = df.loc[df.period==periodo].groupby('treatment').get_group('Z')
    sns.kdeplot(np.repeat(df_P['hour'], df_P['counts']), ax=ax[idx], color=plt_colors['P'])
    sns.kdeplot(np.repeat(df_Z['hour'], df_Z['counts']), ax=ax[idx], color=plt_colors['Z'])
    ax[idx].set_xlabel('Hora')
    ax[idx].set_ylabel('Actividad acústica normalizada')
    ax[idx].set_title(f'Especie: {sp_focal} - periodo: {periodo}')
    ax[idx].set_xlim([0, 24])
    
sns.despine(trim=True)
fig.tight_layout()
plt.savefig(f'../../output/figures/detections/temporal_activity_kde_{sp_focal}.png')

#%% TEMPORAL ACTIVITY FOR METRICS IN OVERLAP - R PACKAGE
#path_detections_compiled = '../../output/detections/custom_detections_compiled.csv'
path_detections_compiled = '../../output/detections/birdnet_detections_compiled.csv'
path_metadata = '../../output/metadata/metadata_t0-t1-t2.csv'
sp_focal = 'grekis'  # ['ENGPUS', 'peptyr1', 'grekis']
birdnet_confidence_th = 0.4

df_metadata = pd.read_csv(path_metadata)
df_annot = pd.read_csv(path_detections_compiled)

# select columns
df = df_annot[['Species Code', 'Confidence', 'fname']]
# select species
df = df.loc[df_annot['Species Code'] == sp_focal,:]
# filter by confidence
df = df.loc[(df.Confidence>=birdnet_confidence_th)]
# merge with metadata
df = df.merge(df_metadata[['fname', 'site', 'day', 'time', 'period']], on='fname')
df['site'] = df['site'].str[0:2]
df['treatment'] = df['site'].str[0]

df['Time'] = df['time']/240000
df.rename(columns={'Species Code': 'Sps'}, inplace=True)
df['Zone'] = df['period'] + '_'+ df['treatment']
df.to_csv(f'../../output/detections/{sp_focal}_temporal_raw.csv', index=False)
