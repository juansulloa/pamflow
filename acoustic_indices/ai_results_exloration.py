""" 
Evaluate the results of the acoustic indices and plot

"""
#%%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt_colors = {'T0': '#2b8cbe',
              'T1': '#7bccc4',
              'T2': '#ccebc5',
              'P': '#f1a340',
              'Z': '#998ec3',
              'Pozo': '#f1a340',
              'Control': '#998ec3',
              'P6-t0': '#2b8cbe',
              'P6-t2': '#ccebc5',}

acoustic_indices = ['ADI', 'ACI', 'NDSI', 'BI', 'Hf', 'Ht', 'H', 'SC', 'NP']

#%% PLOT OVERVIEW OF VARIATION OF INDICES
df = pd.read_csv('../../output/dataframes_ai/ai_compiled.csv')
df.rename(columns={'SC_MF': 'SC'}, inplace=True)
df.drop(columns=['SC_HF'], inplace=True)
df['sites'] = df['sensor_name'].str[0:2] + '-' + df['period']
df = df.loc[~df.sensor_name.isin(['P3-G035', 'P4-G033'])]

# plot g
fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
ax = ax.ravel()
for i, aindex in enumerate(acoustic_indices):
    sns.regplot(df, x='hour', y=aindex, order=6, scatter=False, ax=ax[i])
    ax[i].set_title(aindex)
    ax[i].set_ylabel('')

sns.histplot(df, x='SC', bins=100, hue='day_period', kde=True)

plt_data = df.loc[df.day_period=='night',:].groupby('sites').mean()
plt_data.reset_index(inplace=True)
plt_data['Tratamiento'] = plt_data.sites.str[0].replace({
    'P': 'Pozo',
    'Z': 'Control'
})

fig, ax = plt.subplots()
sns.scatterplot(plt_data, x='NDSI', y='SC', hue='Tratamiento', 
                palette=plt_colors, ax=ax, s=70)
# Annotate each point with the corresponding text
for i, txt in enumerate(plt_data['sites']):
    ax.annotate(txt, (plt_data['NDSI'][i]-0.01, plt_data['SC'][i]+0.01), 
                fontsize='x-small', color='gray')
sns.despine()

#%% PLOT - grid plotting each index in t0 t1 and t2, for each site
df = pd.read_csv('../../output/dataframes_ai/ai_compiled_mean.csv')
df.rename(columns={'SC_MF': 'SC'}, inplace=True)
acoustic_indices = df.drop(
    columns=['sensor_name', 'period', 'day_period', 'SC_HF']).columns.values

plt_data = df.loc[df.sensor_name.str.startswith('P6'),:]

for site in df.sensor_name.unique():
    plt_data = df.loc[df.sensor_name==site,:]
    fig, ax = plt.subplots(3,3)
    ax = ax.ravel()
    for i, aindex in enumerate(acoustic_indices):
        sns.lineplot(plt_data, x='period', y=aindex, hue='day_period', markers=True, 
                    style='day_period', palette=plt_colors, dashes=True, ax=ax[i])
        ax[i].set_ylabel('')
        ax[i].set_xlabel('')
        ax[i].legend([],[], frameon=False)
        ax[i].set_title(aindex)
    sns.despine()
    fig.set_tight_layout(tight=True)
    plt.savefig(f'../../output/figures/acoustic_indices/{site}.png')

#%% PLOT - diferencia entre t0 y t2

df = pd.read_csv('../../output/dataframes_ai/ai_compiled_mean.csv')
df.rename(columns={'SC_MF': 'SC'}, inplace=True)
df = df.groupby('day_period').get_group('night')
df = df.loc[df.period.isin(['t0', 't2'])]
df_pivot = df.pivot(index='sensor_name', columns='period')
# Calculate the differences between t1 and t0 for each acoustic_index
df_diff = df_pivot['ADI']['t2'] - df_pivot['ADI']['t0']
df_diff = pd.DataFrame(df_diff, columns=['ADI'])
# Repeat for other features
for aindex in df.columns[3:]:
    diff_col = aindex
    df_diff[diff_col] = df_pivot[aindex]['t2'] - df_pivot[aindex]['t0']

df_diff['dist'] = [600, 500, 400, 300, 200, 100, 500, 400, 300, 200, 100]
df_diff['Tratamiento'] = df_diff.index.str[0]
df_diff.drop(index=['P3-G035', 'P4-G033'], inplace=True)

# plot
fig, ax = plt.subplots(3,3, sharex=True)
ax = ax.ravel()
for i, aindex in enumerate(acoustic_indices):
    plt_data = df_diff[[aindex, 'dist', 'Tratamiento']]
    sns.lineplot(plt_data, x='dist', y=aindex, hue='Tratamiento', markers=True, 
                        style='Tratamiento', palette=plt_colors, dashes=True, ax=ax[i])
    ax[i].set_title(aindex)
    ax[i].set_xlabel('')
    ax[i].set_xticks([100, 200, 300, 400, 500, 600])
    ax[i].set_xticklabels([100,200,300,400,500,600], rotation=45)
    ax[i].set_ylabel('')
    ax[i].legend([],[], frameon=False)
    
ax[7].set_xlabel('Distancia')
ax[3].set_ylabel('Valor índice')
sns.despine(trim=True)
fig.set_tight_layout(tight=True)