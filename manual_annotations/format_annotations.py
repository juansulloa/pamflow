""" 
Process manual annotations, combine into a single dataframe, compute proportions and plot results

"""

#%%  ----------------------- Load libraries and functions --------------------------
import pandas as pd
import numpy as np
import glob
import os

# Functions
def compute_proportions(events_df, timeline_start, timeline_end, timeline_step):
    """ Compute proportion of presence of events """

    # Step 1: Generate a Timeline
    timeline = pd.DataFrame({
        'time': np.arange(timeline_start, timeline_end, timeline_step),
        'presence': False
        })

    # Step 2: Identify Time Gaps
    for event_start, event_end in zip(events_df['Begin Time (s)'], events_df['End Time (s)']):
        idx = (event_start  - timeline_step <= timeline.time) & (timeline.time <= event_end)
        timeline.loc[idx, 'presence'] = True

    # Step 3: Calculate Proportion
    # print(f"Proportion of events presence:\n {timeline.presence.value_counts() / len(timeline)}")
    #return timeline.presence.value_counts() / len(timeline)
    return timeline

# Variables 
tipo_dict = {
    'AN': 'ANT',
    'IO': 'BIO',
    ' BIO': 'BIO',
    'BIO ': 'BIO',
}

id_dict = {
    'AVEVOV': 'AVEVOC',
    'AEVOC': 'AVEVOC',
    'AVEOC': 'AVEVOC',
    'MURCI': 'MURCIE',
    'MURCIE ': 'MURCIE',
    'OTRO': 'INDETE',
    'VOZ': 'VOZHUM',
    'HRPET': 'HERPET'
    }

det_dict = {
    # Herpetos
    'LRPFUS':'LEPFUS',
    'SCICAP': 'SCIROS',
    'BOSPUG': 'BOAPUG',
    # Murcis
    'MYO_SP': 'MYO_01',
    'MOLOS_02': 'MOLOS_01',
    'MOL_01': 'MOL_SP1',
    'EPT__01': 'EPT_01',
    'EUMGLAU': 'EUMGLA',
    # Aves
    ' BROJUG': 'BROJUG',
    'ATAPIL': 'ATRPIL',
    'ATRA': 'ATRPIL',
    'ATRAPIL': 'ATRPIL',
    'AVE-SP1': 'AVE_SP1',
    'BROJU': 'BROJUG',
    'CAMPGRI': 'CAMGRI',
    'CANGRI': 'CAMGRI',
    'CROANI': 'CROMAJ', # ??
    'CYNGJU': 'CYCGUJ',
    'EUPTIR': 'EUPTRI',
    'FLAPIC': 'FLUPIC',
    'HYPFLA': 'HYLFLA',
    'INECAU ': 'INECAU',
    'NENEMPIL': 'NEMPIL',
    'NYCABL': 'NYCALB',
    'PARCAY': 'PATCAY',
    'PENSAR': 'INDETE', # ??
    'PISUL': 'PITSUL',
    'PITSU': 'PITSUL',
    'PITUSL': 'PITSUL',
    'SAOLI': 'SALOLI',
    'SINCAN': 'SYNCAN',
    'TAPANAE': 'TAPNAE',
    'TAPNAE ': 'TAPNAE',
    'THRPL': 'THRPAL',
    'THRPLA': 'THRPAL',
    'THYRMEL': 'TYRMEL',
    'TOLFA': 'TOLFLA',
    'TOLFAL': 'TOLFLA',
    'TOLFL': 'TOLFLA',
    'TRYMEL': 'TYRMEL',
    'TYRMAL': 'TYRMEL',
    'TYRMLEL': 'TYRMEL',
    'VANCH': 'VANCHI'
}


#%%  ----------------------- LOAD AND FORMAT DATA  --------------------------

flist = glob.glob('../../input/mannot/**/*selections.txt')
df = pd.DataFrame()
for file in flist:
    aux = pd.read_csv(file, sep='\t', encoding='latin1')
    # remove Waveform View
    aux = aux.loc[aux.View == 'Spectrogram 1']  
    # format columns
    uppercase_columns = [col.upper()[0:3] for col in aux.columns]
    aux.rename(columns={
        aux.columns[uppercase_columns.index('DET')]: 'DET',
        aux.columns[uppercase_columns.index('TIP')]: 'TIPO',
        aux.columns[uppercase_columns.index('ID')]: 'ID',
        },
        inplace=True)
    aux = aux[['Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 
                'TIPO', 'ID', 'DET']]
    aux['fname'] = os.path.basename(file)
    # concat
    df = pd.concat([df, aux], ignore_index=True)

df.TIPO.replace(
    tipo_dict,
    inplace=True,
)

df.ID.replace(
    id_dict,
    inplace=True,
)

df.DET.replace(
    det_dict,
    inplace=True,
)

df.dropna(inplace=True)
df.to_csv('../../output/dataframes_mannot/compiled_mannot.csv', index=False)


#%% REVISE MANUALLY AND FIX TYPO ERRORS
"""
df_codes_sp = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='ALL_SP_CODES')
df_codes_global = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='TAXONOMÍA GLOBAL')

# Validate TIPO
df.TIPO.value_counts()
print("Selections not in TIPO: \n", df.loc[~df.TIPO.isin(df_codes_global.CODIGO_TIPO.unique())])

# Validate ID
df.ID.value_counts()
print("Selections not in TIPO: \n", df.ID.loc[~df.ID.isin(df_codes_global.CODIGO_ID.unique())])

# Validate Determinacion
df.DET.value_counts()
print("Selections not in TIPO: \n", df.DET.loc[~df.DET.isin(df_codes_sp.CODIGO)].unique())
"""

#%% Compute proportions
df = pd.read_csv('../../output/dataframes_mannot/compiled_mannot.csv')
df_codes_sp = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='ALL_SP_CODES')
df_codes_global = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='TAXONOMÍA GLOBAL')

tstart, tend, tstep = [0, 480, 10]
time_index = pd.DataFrame({
    'timelapse': np.arange(tstart, tend, tstep),
    'real': pd.date_range(
        start='00:00:00', end='23:59:59', freq='30T').strftime(date_format='%H:%M')
})

# Remove samples that overlap with Noise
df = df.loc[(df['Low Freq (Hz)'] > 2000),:]

# global - TIPO
df_prop_tipo = pd.DataFrame()
for fname in df.fname.unique():
    df_file = df.loc[df.fname==fname]
    df_prop = pd.DataFrame()
    df_prop['time'] = time_index['timelapse']
    df_prop['fname'] = fname
    # for each soundscape element
    for code in ['BIO', 'ANT', 'GEO']:
        aux_prop = compute_proportions(
            df_file[df_file.TIPO == code], tstart, tend, tstep)['presence'].astype(int)
        aux_prop.name = code
        df_prop = pd.concat([df_prop, aux_prop], axis=1)

    df_prop_tipo = pd.concat([df_prop_tipo, df_prop], axis=0)

df_prop_tipo.to_csv('../../output/dataframes_mannot/proportions_tipo.csv', index=False)

# global - ID
df_prop_global = pd.DataFrame()
for fname in df.fname.unique():
    df_file = df.loc[df.fname==fname]
    df_prop = pd.DataFrame()
    df_prop['time'] = time_index['timelapse']
    df_prop['fname'] = fname
    # for each soundscape element
    for idx, code in df_codes_global['CODIGO_ID'].items():
        aux_prop = compute_proportions(
            df_file[df_file.ID == code], tstart, tend, tstep)['presence'].astype(int)
        aux_prop.name = code
        df_prop = pd.concat([df_prop, aux_prop], axis=1)

    df_prop_global = pd.concat([df_prop_global, df_prop], axis=0)

df_prop_global.to_csv('../../output/dataframes_mannot/proportions_id.csv', index=False)

# especies - DET
df_prop_allsp = pd.DataFrame()
for fname in df.fname.unique():
    df_file = df.loc[df.fname==fname]
    df_prop = pd.DataFrame()
    df_prop['time'] = time_index['timelapse']
    df_prop['fname'] = fname
    # for each species
    for idx, code in df_codes_sp['CODIGO'].items():
        aux_prop = compute_proportions(
            df_file[df_file.DET == code], tstart, tend, tstep)['presence'].astype(int)
        aux_prop.name = code
        df_prop = pd.concat([df_prop, aux_prop], axis=1)

    df_prop_allsp = pd.concat([df_prop_allsp, df_prop], axis=0)

df_prop_allsp.to_csv('../../output/dataframes_mannot/proportions_species.csv', index=False)


#%% COMPUTE BIOACOUSTIC INDEX WITH AREA

df = pd.read_csv('../../output/dataframes_mannot/compiled_mannot.csv')
df_codes_sp = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='ALL_SP_CODES')
df_codes_global = pd.read_excel('../../input/mannot/sp_codes.xlsx', sheet_name='TAXONOMÍA GLOBAL')

# Remove samples that overlap with Noise
df = df.loc[(df['Low Freq (Hz)'] > 2000),:]

# Get only BIO
df = df.loc[df.TIPO=='BIO']

# global - TIPO
df_area_tipo = pd.DataFrame()
area_total = 480*96000 # tiempo total 480 x 96000 kHz
for fname in df.fname.unique():
    df_file = df.loc[df.fname==fname]
    area_bio = (df_file['End Time (s)'] - df_file['Begin Time (s)']) * (df_file['High Freq (Hz)'] - df_file['Low Freq (Hz)'])
    area_bio_total = area_bio.sum() / area_total * 100
    df_prop = pd.DataFrame({'fname': fname,
                            'bio': area_bio_total}, index=[0])
    df_area_tipo = pd.concat([df_area_tipo, df_prop], axis=0, ignore_index=True)

df_area_tipo.reset_index(inplace=True, drop=True)
df_area_tipo['site'] = df_area_tipo['fname'].str[0:2]
df_area_tipo['day'] = df_area_tipo['fname'].str[8:13]
df_area_tipo['period'] = df_area_tipo['fname'].str[8:10].replace({'04': 't0', 
                                                                     '05': 't2',
                                                                     '06': 't2'})

df_area_tipo.to_csv('../../output/dataframes_mannot/biofonia_area_index.csv', index=False)