""" 
proportions_tipo_all.csv # sin filtrar a 2


"""
#%% Init packages, functions and variables
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Variables
period_dict = {'04': 'T0',
               '05': 'T2',
               '06': 'T2'}

plt_colors = {'T0': '#2b8cbe',
              'T1': '#7bccc4',
              'T2': '#ccebc5',
              't0': '#2b8cbe',
              't1': '#7bccc4',
              't2': '#ccebc5',}


codes = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='TAXONOMÍA GLOBAL')
sp_codes = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='ALL_SP_CODES')
dict_tipo = codes.set_index('CODIGO_TIPO')['TIPO'].to_dict()
dict_id = codes.set_index('CODIGO_ID')['ID'].to_dict()
dict_sp = sp_codes.set_index('CODIGO')['ESPECIE'].to_dict()

#%% PLOT GLOBAL PROPORTIONS PER SITE
df_global_all = pd.read_csv('../../output/dataframes_mannot/proportions_tipo_all.csv')
#df_global = pd.read_csv('../../output/dataframes_mannot/proportions_tipo.csv')

plt_data = df_global_all.drop(columns='time').groupby('fname').mean()
plt_data['Sitio'] = plt_data.index.str[0:2]
plt_data['Periodo'] = plt_data.index.str[8:10]
plt_data['Periodo'].replace(period_dict, inplace=True)
plt_data.rename(columns=dict_tipo, inplace=True)

fig, ax = plt.subplots(1,3, figsize=[8,3.5], sharey=True)
sns.boxplot(plt_data, x='Sitio', y='Biofonía', hue='Periodo', 
            ax=ax[0], palette=plt_colors, linewidth=0.75)
ax[0].set_ylim(0,1)
ax[0].set_ylabel('Proporción')
ax[0].legend([],[], frameon=False)
ax[0].set_title('Biofonía')

#plt_data = df_global_all.drop(columns='time').groupby('fname').mean()
#plt_data['Sitio'] = plt_data.index.str[0:2]
#plt_data['Periodo'] = plt_data.index.str[8:10]
#plt_data['Periodo'].replace(period_dict, inplace=True)
#plt_data.rename(columns=dict_tipo, inplace=True)

sns.boxplot(plt_data, x='Sitio', y='Antropofonía', hue='Periodo', 
            ax=ax[1], palette=plt_colors,linewidth=0.75)
ax[1].set_ylim(0,1)
ax[1].legend([],[], frameon=False)
ax[1].set_ylabel('')
ax[1].set_title('Antropofonía')

sns.boxplot(plt_data, x='Sitio', y='Geofonía', hue='Periodo', 
            ax=ax[2], palette=plt_colors, linewidth=0.75)
ax[2].set_ylim(0,1)
ax[2].set_title('Geofonía')
ax[2].set_ylabel('')
sns.despine(trim=True)
fig.set_tight_layout(tight=True)

plt.savefig('../../output/figures/tipo_proportions_all.png')

#%% PLOT PATTERNS BIOFONIA
df_id = pd.read_csv('../../output/dataframes_mannot/proportions_id_all.csv')

plt_data = df_id.drop(columns='time').groupby('fname').mean()
plt_data['Sitio'] = plt_data.index.str[0:2]
plt_data['Periodo'] = plt_data.index.str[8:10]
plt_data['Periodo'].replace(period_dict, inplace=True)
plt_data['Zona'] = plt_data['Sitio'].str[0]
plt_data.rename(columns=dict_id, inplace=True)


fig, ax = plt.subplots(2,2, figsize=[8,6])
ax = ax.ravel()

sns.boxplot(plt_data, x='Sitio', y='Insectos', hue='Periodo', 
            ax=ax[0], palette=plt_colors,linewidth=0.75)
ax[0].set_ylim(0,1)
ax[0].set_ylabel('')
ax[0].set_xlabel('')
ax[0].legend([],[], frameon=False)
ax[0].set_title('Insectos')

sns.boxplot(plt_data, x='Sitio', y='Aves', hue='Periodo', 
            ax=ax[1], palette=plt_colors, linewidth=0.75)
ax[1].set_ylim(0,1)
ax[1].set_ylabel('Proporción')
ax[1].set_xlabel('')
ax[1].legend([],[], frameon=False)
ax[1].set_title('Aves')

sns.boxplot(plt_data, x='Sitio', y='Murciélago', hue='Periodo', 
            ax=ax[2], palette=plt_colors, linewidth=0.75)
ax[2].set_ylim(0,1)
ax[2].set_ylabel('Proporción')
ax[2].set_title('Murciélagos')
ax[2].legend([],[], frameon=False)

sns.boxplot(plt_data, x='Sitio', y='Herpetos', hue='Periodo', 
            ax=ax[3], palette=plt_colors, linewidth=0.75)
ax[3].set_ylim(0,1)
ax[3].set_ylabel('')
ax[3].set_title('Anfibios')

sns.despine(trim=True)
fig.set_tight_layout(tight=True)

plt.savefig('../../output/figures/id_proportions.png')

#%% PLOT SPECIES VS MINIMUM FREQUENCY
df = pd.read_csv('../../output/dataframes_mannot/compiled_mannot.csv')
plt_data = df.loc[(df.TIPO=='BIO') & (df['Low Freq (Hz)'] < 4000),]
plt_data['DET'].replace(dict_sp, inplace=True)

# Aves
plt_aux = plt_data.loc[plt_data.ID=='AVEVOC',:]
sort_idx = plt_aux.groupby('DET')['Low Freq (Hz)'].median().sort_values().index
fig, ax = plt.subplots(figsize=[10,15])
sns.boxplot(data=plt_aux, y='DET', x='Low Freq (Hz)',
            color='#99d8c9', linewidth=0.75, fliersize=0.2, order=sort_idx, ax=ax)
ax.axvline(3000, color=".3", dashes=(2, 2))
ax.set_ylabel('')
sns.despine()
fig.set_tight_layout(tight=True)

# Anfibios
plt_aux = plt_data.loc[plt_data.ID=='HERPET',:]
sort_idx = plt_aux.groupby('DET')['Low Freq (Hz)'].median().sort_values().index
fig, ax = plt.subplots(figsize=[10,3])
sns.boxplot(data=plt_aux, y='DET', x='Low Freq (Hz)',
            color='#99d8c9', linewidth=0.75, fliersize=0.2, order=sort_idx, ax=ax)
ax.axvline(3000, color=".3", dashes=(2, 2))
ax.set_ylabel('')
sns.despine()
fig.set_tight_layout(tight=True)


sns.catplot(data=plt_data, y='DET', x='Low Freq (Hz)', hue='ID', 
            palette='Set2', linewidth=0.3, kind='violin', ax=ax)


#%% SPECIES ABUNDANCE PLOT
df = pd.read_csv('../../output/dataframes_mannot/proportions_species_all.csv')
xx = df.drop(columns=['time', 'fname']).sum(axis=0).sort_values()

#%% INDVAL PLOT
df = pd.read_csv('../../output/dataframes_mannot/indicator_species_results.csv')
df['species'].replace(dict_sp, inplace=True)
sns.barplot(df, y='species', x='indval', hue='group')

#%% BIOPHONY AREA

df_area_tipo = pd.read_csv('../../output/dataframes_mannot/biofonia_area_index.csv')

fig, ax = plt.subplots()
sns.boxplot(df_area_tipo, x='site', y='bio', hue='period', order=['P6', 'P5', 'Z6', 'Z5'],
            palette=plt_colors, linewidth=0.75, ax=ax)
ax.set_xlabel('Punto de muestreo')
ax.set_ylabel('Biofonía (%)')
plt.legend(title='Periodo')
sns.despine(trim=True)
plt.savefig('../../output/figures/biophony_area.png')