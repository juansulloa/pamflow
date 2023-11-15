#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Geo Database for PaisajesSonorosTB
----------------------------------------

This script compiles output from multiple scripts that should be executed previously:
    - audio_metadata
    - acoustic_indices
    - graphical_soundscapes
    - soundscape_composition

"""

import pandas as pd
import glob
import os

#%% Load acoustic indices, graphical soundscapes, and manual annotations to build the GDB

# Audio metadata
df_metadata = pd.read_csv('../../output/metadata/metadata_t0-t1-t2.csv')
df_metadata['site'] = df_metadata['period'] + '_' + df_metadata['site']

# Acoustic indices
df_indices = pd.read_csv('../../output/dataframes_ai/ai_compiled_mean.csv')
df_indices.rename(columns={'SC_MF': 'SC', 'sensor_name': 'site'}, inplace=True)
df_indices['site'] = df_indices['period'] + '_' + df_indices['site']

# Graphical soundscapes
df_graph = pd.read_csv('../../output/dataframes_gs/gs_compiled_dataframe_2-24kHz.csv', sep=' ')
df_graph.reset_index(inplace=True)
df_graph.rename(columns={'index': 'site'}, inplace=True)

# Soundscape components using manual annotations
df_comp = pd.read_csv('../../output/dataframes_mannot/proportions_tipo_all.csv')
df_comp['site'] = df_comp.fname.str.split('_').str[1].str[0:2].replace({'04': 't0', '05': 't2', '06': 't2'}) + '_' + df_comp.fname.str.split('_').str[0]

# Geographic data
df_coord = pd.read_csv('../../input/sensor_deployment.csv')
df_coord.rename(columns={'Punto': 'sensor_name'}, inplace=True)
df_coord.drop(columns=['No', 'Inicio', 'Fin', 'Hora instalacion', 'comentario'], inplace=True)

#%% Process dataframes to meet GDB criteria

# Compute metadata per site
df_site_metadata = pd.DataFrame()
for site_idx, site in df_metadata.groupby('site'):
    site_metadata = pd.Series({'site': site_idx,
                               'sensor_name': site_idx.split('_')[1],
                               'TASA_MUEST': site['sample_rate'].unique()[0].astype(int),
                               'RES_BITS': site['bits'].unique()[0].astype(int),
                               'MICROFONO': 'Audiomoth v1.20',
                               'REF_GRAB': 'Audiomoth v1.20',
                               'FECHA_INI': site.date.sort_values().iloc[0][0:10],
                               'FECHA_FIN': site.date.sort_values().iloc[-1][0:10], 
                               'HORA_INI': site.date.sort_values().iloc[0][11:],
                               'HORA_FIN': site.date.sort_values().iloc[-1][11:],
                               'NUM_GRAB': len(site),
                               'TASA_GRAB': '60 segundos cada 1740 segundos',
                               'ALTURA': 1.5
                               })
    df_site_metadata = pd.concat([df_site_metadata, pd.DataFrame([site_metadata])],
                                ignore_index=True)

# Compute proportion of components per site
df_comp['sensor_name'] = df_comp['site']
df_site_comp = pd.DataFrame()
for site_idx, site in df_comp.groupby('sensor_name'):
    site_comp = pd.Series({'site': site_idx,
                           'GEOFONIA': (site['GEO'].mean() * 100).round(3),
                           'ANTROPOFONIA': (site['ANT'].sum()/len(site) * 100).round(3),
                           'BIOFONIA': (site['BIO'].sum()/len(site) * 100).round(3)
                           })

    df_site_comp = pd.concat([df_site_comp, pd.DataFrame(site_comp).T], ignore_index=True)

# Acoustic indices per site
df_site_indices = pd.DataFrame()
for site_idx, site in df_indices.groupby('site'):
    site_indices = pd.Series({'site': site_idx,
                              'ADI_dia': site.loc[site.day_period=='day','ADI'].values[0],
                              'ADI_noche': site.loc[site.day_period=='night','ADI'].values[0],
                              'ACI_dia': site.loc[site.day_period=='day','ACI'].values[0],
                              'ACI_noche': site.loc[site.day_period=='night','ACI'].values[0],
                              'NDSI_dia': site.loc[site.day_period=='day','NDSI'].values[0],
                              'NDSI_noche': site.loc[site.day_period=='night','NDSI'].values[0],
                              'BI_dia': site.loc[site.day_period=='day','BI'].values[0],
                              'BI_noche': site.loc[site.day_period=='night','BI'].values[0],
                              'Hf_dia': site.loc[site.day_period=='day','Hf'].values[0],
                              'Hf_noche': site.loc[site.day_period=='night','Hf'].values[0],
                              'Ht_dia': site.loc[site.day_period=='day','Ht'].values[0],
                              'Ht_noche': site.loc[site.day_period=='night','Ht'].values[0],
                              'H_dia': site.loc[site.day_period=='day','H'].values[0],
                              'H_noche': site.loc[site.day_period=='night','H'].values[0],
                              'SC_dia': site.loc[site.day_period=='day','SC'].values[0],
                              'SC_noche': site.loc[site.day_period=='night','SC'].values[0],
                              'NP_dia': site.loc[site.day_period=='day','NP'].values[0],
                              'NP_noche': site.loc[site.day_period=='night','NP'].values[0],
                              })
    df_site_indices = pd.concat([df_site_indices, pd.DataFrame([site_indices])],
                                ignore_index=True)

#%% Build GDB
df_gdb = df_coord.merge(df_site_metadata, on='sensor_name')
df_gdb = df_gdb.merge(df_site_indices, on='site')
df_gdb = df_gdb.merge(df_site_comp, on='site', how='outer')
df_gdb.to_csv('../../output/gdb/gdb_site.csv', index=False)