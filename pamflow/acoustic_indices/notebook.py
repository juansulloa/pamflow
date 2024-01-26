"""
Postprocess acoustic indices

"""
#%%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import glob
#%%
def plot_acoustic_indices(df, alpha=0.5, size=3):
    # format data
    df['date'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df['time'] = df.date.dt.hour
    # plot
    fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
    sns.scatterplot(df, x='time', y='ACI', alpha=alpha, size=size, ax=ax[0,0])
    sns.scatterplot(df, x='time', y='ADI', alpha=alpha, size=size, ax=ax[0,1])
    sns.scatterplot(df, x='time', y='BI', alpha=alpha, size=size, ax=ax[0,2])
    sns.scatterplot(df, x='time', y='H', alpha=alpha, size=size, ax=ax[1,0])
    sns.scatterplot(df, x='time', y='Ht', alpha=alpha, size=size, ax=ax[1,1])
    sns.scatterplot(df, x='time', y='Hf', alpha=alpha, size=size, ax=ax[1,2])
    sns.scatterplot(df, x='time', y='NDSI', alpha=alpha, size=size, ax=ax[2,0])
    sns.scatterplot(df, x='time', y='NP', alpha=alpha, size=size, ax=ax[2,1])
    sns.scatterplot(df, x='time', y='SC', alpha=alpha, size=size, ax=ax[2,2])
    fig.set_tight_layout('tight')

def summary_stats(df_indices):
    """ Take mean per site, per day-period (day and night) """
    df_indices['date'] = pd.to_datetime(df_indices['date'])

    # Create a new column 'day_night' based on the time of day
    df_indices['day_night'] = df_indices['date'].apply(lambda x: 'day' if 6 <= x.hour < 18 else 'night')

    df_out = pd.concat([
        df_indices[indices_names].median().rename(lambda x: f'{x}_med'),
        df_indices[indices_names].std().rename(lambda x: f'{x}_std'),
        df_indices.loc[df_indices.day_night=='day', 
                    indices_names].median().rename(lambda x: f'{x}_day'),
        df_indices.loc[df_indices.day_night=='night', 
                    indices_names].median().rename(lambda x: f'{x}_nit')
        ])
    return df_out

#%% Plot indices to check consistency
df_indices = pd.read_csv('../../../output/dataframes_ai/H26_indices.csv')
df_metadata = pd.read_csv('../../../output/metadata/metadata_clean_30T.csv', dtype={'time': str})
df_indices = df_indices.merge(df_metadata, on='fname')

plot_acoustic_indices(df_indices, alpha=0.3, size=0.5)


#%% Compute summary statistics per site
indices_names = ['ACI', 'ADI', 'BI', 'H', 'Hf', 'Ht', 'NDSI', 'NP', 'SC']
df_metadata = pd.read_csv('../../../output/metadata/metadata_clean_30T.csv')
flist = glob.glob('../../../output/dataframes_ai/per_site/*_indices.csv')

df_compiled = list()
for fname in flist:
    df_indices = pd.read_csv(fname)
    df_indices = df_indices.merge(df_metadata, on='fname')
    df_out = summary_stats(df_indices)
    df_out.name = df_indices.sensor_name[0]
    df_compiled.append(df_out)

df_compiled = pd.concat(df_compiled, axis=1).T
df_compiled.to_csv('../../../output/dataframes_ai/all_sites_summary_indices.csv')