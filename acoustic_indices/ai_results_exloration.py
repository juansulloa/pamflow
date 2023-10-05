""" 
Evaluate the results of the acoustic indices

TODO
    - Ajustar P6 - t2 en archivo compilado
"""
import pandas as pd
import seaborn as sns

df = pd.read_csv('../../output/dataframes_ai/ai_compiled.csv')
df.sensor_name = df.sensor_name.str[0:2]
df = df.loc[~df.sensor_name.isin(['P3', 'P4']),:]
df = df.loc[df.day_period.isin(['night']),:]

plot_order = ['P6', 'P5', 'P2', 'P1', 'Z6', 'Z5', 'Z4', 'Z3', 'Z2']
#df_t0 = pd.read_csv('../../output/metadata/metadata_t0_P5_P6_Z5_Z6.csv')
#df = df.loc[df.fname.isin(df_t0.fname),:]


sns.set_theme(style="ticks", palette="colorblind")
sns.boxplot(data=df, x='sensor_name', y='SC_MF', hue='period', order=plot_order)
sns.boxplot(data=df, x='sensor_name', y='NP', hue='period', order=plot_order)
sns.boxplot(data=df, x='sensor_name', y='BI', hue='period', order=plot_order)


#%%
df = pd.read_csv('../../output/dataframes_ai/ai_compiled.csv')
df.groupby('sensor_name').get_group('Z6-G047')