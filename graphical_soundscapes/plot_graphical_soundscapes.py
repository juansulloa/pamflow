# Plot graphical soundscapes

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

flist = glob.glob('../../output/dataframes_gs/python_gs/*.csv')

df = pd.DataFrame()
for fname in flist:
    aux = pd.read_csv(fname)
    aux.drop(columns='time', inplace=True)
    aux = pd.Series(aux.values.ravel(), name=fname[-17:-12])
    df = df.append(aux)

# plot huella acústica promedio - todos
plt_data = df.mean().values
fig, ax = plt.subplots()
ax.imshow(plt_data.reshape([24, 128]).T, aspect='auto', origin='lower', extent=[0, 24, 0, 24])
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Frecuencia (kHz)')

# plot huella acústica promedio - cerca al pozo t0
plt_data = df.loc[df.index.isin(['t0_P5', 't0_P6']),:].mean().values
fig, ax = plt.subplots()
ax.imshow(plt_data.reshape([24, 128]).T, aspect='auto', origin='lower', extent=[0, 24, 0, 24])
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Frecuencia (kHz)')

# plot huella acústica promedio - P1 P2 t0
plt_data = df.loc[df.index.isin(['t0_P1', 't0_P2']),:].mean().values
fig, ax = plt.subplots()
ax.imshow(plt_data.reshape([24, 128]).T, aspect='auto', origin='lower', extent=[0, 24, 0, 24])
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Frecuencia (kHz)')

# plot huella acústica promedio - Z6 - Z5
plt_data = df.loc[df.index.isin(['t0_Z5', 't0_Z6']),:].mean().values
fig, ax = plt.subplots()
ax.imshow(plt_data.reshape([24, 128]).T, aspect='auto', origin='lower', extent=[0, 24, 0, 24])
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Frecuencia (kHz)')

# plot huella acústica promedio - cerca al pozo t2
plt_data = df.loc[df.index.isin(['t2_Z5', 't2_Z6']),:].mean().values
fig, ax = plt.subplots()
ax.imshow(plt_data.reshape([24, 128]).T, aspect='auto', origin='lower', extent=[0, 24, 0, 24])
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Frecuencia (kHz)')