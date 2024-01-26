from pamflow.classification.utils import match_files, read_annot_files, build_annotated_audio_track

#%% VARIABLES
path_annot = '/Users/jsulloa/Downloads/annot/'
path_audio = '/Users/jsulloa/Downloads/audio/'
n_segments = 10 # number of segments per category
labels = ['blcjay1']  # list, labels that are neeeded to annotate
min_conf = 0.5

# build annotated_audio_track
silence_len = 0.1
path_audio = 'Path Audio'
min_t = 'Begin Time (s)'
max_t = 'End Time (s)'
label = 'Species Code'
path_save = '/Users/jsulloa/Downloads/output/'

#%% Main
# load data
matched_files = match_files(path_annot, path_audio)
df_annot = merge_mannot_files(matched_files.fpath_annot.to_list(), verbose=False)

# filter dataframe
df_annot = df_annot.loc[
    (df_annot['Confidence']>min_conf) & (df_annot['Species Code'].isin(labels))]

# add path audio column
df_annot['Path Audio'] = matched_files.loc[
    df_annot['File Name'].str.split('.').str[0].values,'fpath_audio'].values

# segments
build_annotated_audio_track(df_annot, path_audio, min_t, max_t, silence_len, path_save)
df_annot.to_csv(os.path.join(path_save, 'df_annot.csv'))
