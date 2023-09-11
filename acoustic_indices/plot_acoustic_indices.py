"""
 Custom plot for acoustic indices in 3 treatments
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#%% Exploratory plot - all indices
df_indices = pd.read_csv('../../output/dataframes_ai/P6-G026_indices.csv')

# set variables
df_indices.loc[:,'date_fmt'] = pd.to_datetime(df_indices.date,  format='%Y-%m-%d %H:%M:%S')
df_indices['time'] = df_indices.date.str[11:13].astype(int)
ai_list=['ADI', 'ACI', 'NDSI', 'BI','Hf', 'Ht', 'H', 'SC_MF', 'NP']
alpha=0.3
size=0.5
colors = {'t0': '#006d2c',
          't1': '#2ca25f',
          't2': '#66c2a4'}

plt.close('all')
fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
ax = ax.ravel()
periods = df_indices.period.unique()
for t in periods:
    df_sel = df_indices.loc[df_indices.period==t,:]

    for (i, idx_ax) in enumerate(ax):
        sns.scatterplot(
           df_sel, x='time', y=ai_list[i], alpha=alpha, size=size, color=colors[t],
           ax=idx_ax, legend=False)        
        sns.regplot(
            df_sel, x='time', y=ai_list[i], order=6, scatter=False, color=colors[t],
            ax=idx_ax)
# arrange axes
for idx, ax_aux in enumerate(ax.ravel()):
    ax_aux.set_xticks([0, 6, 12, 18, 24])
    if idx >=6:
        ax_aux.set_xlabel('Time')
    else:
        ax_aux.set_xlabel('')

plt.subplots_adjust(left=0.125, right=0.9, bottom=0.2, top=0.95, wspace=0.35, hspace=0.2)
fig.legend(colors, loc ='lower center')

#%%
"""
Plot single indices at selected periods
"""
import pandas as pd
import seaborn as sns
import glob
import os

fname_csv = glob.glob('../../output/dataframes_ai/P6*.csv')
df_indices = pd.read_csv(fname_csv[0])
df_indices.loc[:,'date_fmt'] = pd.to_datetime(df_indices.date,  format='%Y-%m-%d %H:%M:%S')
df_indices['time'] = df_indices.date.str[11:13].astype(int)

sns.lmplot(
    df_indices, x='time', y='SC_MF', hue='period', order=6, palette='Dark2')

"""
Plot single indices at selected points
"""
sel_sites = ['P6', 'P5', 'Z5', 'Z3']
sel_period = ['t0', 't1']

fname_csv = glob.glob('../../output/dataframes_ai/*.csv')
df_indices = pd.DataFrame()
for fname in fname_csv:
    aux = pd.read_csv(fname)
    aux['site'] = os.path.basename(fname)[0:2]
    df_indices = pd.concat([df_indices, aux], axis=0)

df_indices.loc[:,'date_fmt'] = pd.to_datetime(df_indices.date,  format='%Y-%m-%d %H:%M:%S')
df_indices['time'] = df_indices.date.str[11:13].astype(int)
df_indices = df_indices.loc[(df_indices.site.isin(sel_sites) & 
                             df_indices.period.isin(sel_period)),:]

sns.lmplot(
    df_indices, x='time', y='SC_MF', hue='site', order=6, palette='Dark2')

ax = sns.boxplot( 
    df_indices, x='site', y='BI', hue='time', palette='crest', linewidth=0.1, fliersize=0.1)
ax.legend_.remove()