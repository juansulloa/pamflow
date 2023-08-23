import matplotlib.pyplot as plt
import seaborn as sns
from maad import features, util, sound
import numpy as np
import pandas as pd

df_full = pd.read_csv('../../output/metadata/metadata_full.csv')
df = df_full.groupby('sensor_name').get_group('P6-G026')
df.sort_values('date_fmt', inplace=True)
df.reset_index(drop=True, inplace=True)
df['rms'] = np.nan

for idx, row in df.iterrows():
    print(idx, ':',row.fname)
    s, fs = sound.load(row.path_audio)
    s = sound.select_bandwidth(s, fs, fcut=[1, 3000], forder=6)
    rms_val = util.rms(s)
    df.loc[idx, 'rms'] = rms_val

df.loc[:,'date_fmt'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
df['day'] = df.date_fmt.dt.strftime('%m-%d')
df['week'] = df.date_fmt.dt.week
df['hour'] = df.date_fmt.dt.hour

# Compute decibels relative to the lowest values, for values aggregated by day.
plt_data = df.loc[df.hour.isin([0,1,2,3,4,5]),['day','rms']]
plt_data['db'] = 20*np.log10(plt_data['rms']/plt_data['rms'].min())
fig, ax = plt.subplots(figsize=[10,8])
sns.boxplot(plt_data, x='day', y='db', linewidth=0.2, ax=ax)
ax.grid(alpha=0.5, axis='y')
ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21])
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.set_ylabel('Decibelios relativos al valor mínimo')
ax.set_xlabel('Día')
sns.despine(trim=True)

#%% Select samples for manual analysis
df_full = pd.read_csv('../../output/metadata/metadata_full.csv')
df_full.loc[:,'date_fmt'] = pd.to_datetime(df_full.date,  format='%Y-%m-%d %H:%M:%S')
df_full['day'] = df_full.date_fmt.dt.strftime('%m-%d')
df_full['hour'] = df_full.date_fmt.dt.hour

sites = ['Z5-G034', 'Z6-G047', 'P5-G022', 'P6-G026']
t0 = ['04-13', '04-14', '04-15', '04-16', '04-17', '04-18']
t1 = ['05-02', '05-03', '05-04', '05-05', '05-06', '05-07']
t2 = ['06-01', '06-02', '06-03', '06-04', '06-05', '06-06']
peak_hours = [5, 6, 7, 8, 17, 18, 19, 20]

df_sample_t0 = df_full.loc[
    (df_full.site.isin(sites)) & 
    (df_full.day.isin(t0)) & 
    (df_full.hour.isin(peak_hours)),
    :].sample(frac=1, random_state=123)
df_sample_t0.to_csv('../../output/metadata/metadata_sample_t0.csv')

df_sample_t1 = df_full.loc[
    (df_full.site.isin(sites)) & 
    (df_full.day.isin(t1)) & 
    (df_full.hour.isin(peak_hours)),
    :].sample(frac=1, random_state=123)
df_sample_t1.to_csv('../../output/metadata/metadata_sample_t1.csv')

df_sample_t2 = df_full.loc[
    (df_full.site.isin(sites)) & 
    (df_full.day.isin(t2)) & 
    (df_full.hour.isin(peak_hours)),
    :].sample(frac=1, random_state=123)
df_sample_t2.to_csv('../../output/metadata/metadata_sample_t2.csv')