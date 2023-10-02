"""
Postprocess acoustic indices

1. Create a dataframe with all acoustic indices and an additional column with day or night
2. Create a processed dataframe with 
"""

import pandas as pd
import glob

#%% Set variables
flist = glob.glob('../../output/dataframes_ai/*indices.csv')
day = [6,7,8,9,10,11,12,13,14,15,16,17]

#%% Load data
df = pd.DataFrame()
for fname in flist:
    df = pd.concat([df, pd.read_csv(fname)])

df['hour'] = pd.to_datetime(df.date).dt.hour
df['day_period'] = df.hour.isin(day).replace({False: 'night', True: 'day'})

df.to_csv('../../output/dataframes_ai/ai_compiled.csv', index=False)

#%% Compute mean per sampling site, period and day_period
df_mean = df.drop(columns=['fname', 'date', 'hour']).groupby(['sensor_name', 'period', 'day_period']).mean().reset_index()

df_mean.to_csv('../../output/dataframes_ai/ai_compiled_mean.csv', index=False)

#%% plot
import matplotlib.pyplot as plt
import seaborn as sns
fig, ax = plt.subplots(figsize=[10,12])
sns.boxplot(data=df_mean, x='sensor_name', y='SC_MF', hue='period')