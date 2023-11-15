import pandas as pd
import glob
import os
""" 
Run analyzer on test data

python analyze.py --i /Volumes/lacie_exfat/Parex/3s_dataset/ATRPIL --o /Volumes/lacie_macosx/Dropbox/PostDoc/iavh/2023_Parex/output/detections/test_predictions/ --lat 10.4 --lon -74.3 --threads 4

"""
path_detections = '../../output/detections/test_predictions/*.txt'
threshold = 0.5
sp_code = 'peptyr1'

flist = glob.glob(path_detections)
df_detections = pd.DataFrame()
for fname in flist:
    aux = pd.read_csv(fname, sep='\t')
    aux['fname'] = os.path.basename(fname).replace('.BirdNET.selection.table.txt', '.wav')
    df_detections = pd.concat([df_detections, aux])

true_positive = df_detections.loc[((df_detections['Species Code'] == sp_code) &
                                  (df_detections['Confidence'] >= threshold)),:]

print('False positive rate:', (100 - len(true_positive)) / 100)