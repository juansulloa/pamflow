# Run BirdNet Analyzer

# Prepare environment
conda activate <environment>
cd birdnet

# Run scripts

Use pretrained model to detect bird species
```
python analyze.py --i /Volumes/MANGO/Parex2023/selected_data/P2-G087 --o /Volumes/lacie_macosx/Dropbox/PostDoc/iavh/2023_Parex/output/detections/birds/ --lat 10.4 --lon -74.3 --threads 4
```

Train a custom model with selected species
```
python train.py --i /Volumes/lacie_exfat/Parex/3s_dataset --o /Volumes/lacie_macosx/Dropbox/PostDoc/iavh/2023_Parex/output/detections/custom_models/multispecies_model.tflite --learning_rate 0.001
```

Use custom model on new data
```
python analyze —classifier path_to_classifier —i path_to_data —o path_to_output 

python analyze.py --classifier /Volumes/lacie_macosx/Dropbox/PostDoc/iavh/2023_Parex/output/detections/custom_models/multisp_model_clean.tflite --i /Volumes/MANGO/Parex2023/selected_data/ --o /Volumes/lacie_macosx/Dropbox/PostDoc/iavh/2023_Parex/output/detections/birds_custom/ --threads 12
```

# Bats

```
python train.py --i /Volumes/MANGO/Parex2023/3s_dataset_bats --o /Users/jsulloa/Dropbox/PostDoc/iavh/2023_Parex/output/detections/custom_models/bats_model.tflite --learning_rate 0.01
```
