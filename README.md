# Soundscapes Analysis Template

This repository provides a template for analyzing soundscapes using python. The project was created with the intention of offering an easy-to-use and reproducible framework that can be used by researchers, conservation biologists, citizen scientists, and anyone else interested in ecoacoustics and soundscape ecology.

## Table of Contents

- [Background](#background)
- [Installation Instructions](#installation-instructions)
- [Getting Started](#getting-started)
- [Directory Structure](#directory-structure)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)

## Background

Soundscapes are composed of all sounds occurring in a given habitat, including biological sounds such as animal vocalizations and non-biological sounds like wind and water. Analyzing soundscapes can provide valuable information about species richness, habitat quality, and ecological changes over time. 

The Python programming language has become key for analyzing soundscapes since it is an open-source language and provides numerous scientific libraries for manipulating sound data. This project provides a template for organizing sound data analysis code and provides an example of how to analyze sound recordings in `.wav` format.

## Before you begin

### 1. Download or clone this repository

```bash
git clone https://github.com/juansulloa/pamflow.git
```

### 2. Setup a working environment 
Set up a working environment with Python 3.10.

```bash
conda create -n pamenv python=3.10
conda activate pamenv
```

Go to the directory where the repository is located and install requirements with pip.

```bash
cd ~/pamflow
pip install -r requirements.txt
```

## Getting Started

### 1. Organize directories
Create a folder project where custom scripts and data will be saved.
```bash
python -m pamflow.preprocess.cli build_folder_structure -i <project_folder>
```

### 2. Set configuration
Edit the `config.yaml` file in the root directory to adjust the settings according to your analysis needs. The file is prefilled with default parameters.

### 3. Run scripts
Run the scripts to prepare the data and extract audio features. 

#### 3.1. Preprocessing
**Add file prefix**
```bash
python -m pamflow.preprocess.cli add_file_prefix -i <input_audio_dir> -r
```
**Get metadata**
```bash
python -m pamflow.preprocess.cli get_audio_metadata -i <input_audio_dir> -o <output_metadata_csv>
```
**Plot sensor deployment and summary overview**
```bash
python -m pamflow.plot.cli sensor_deployment -i <input_metadata_csv>
python -m pamflow.preprocess.cli metadata_summary -i <input_metadata_csv> -o <output_metadata_csv>
```
**Timelapse**
```bash
python -m pamflow.preprocess.cli audio_timelapse -i <input_metadata_csv> -o <output_dir> -c config.yaml
python -m pamflow.plot.cli spectrogram -i <input_dir>   # plot spectrogram of audio timelapse
```

#### 3.2. Compute acoustic indices
```bash
python -m pamflow.acoustic_indices.cli -i <input_metadata_csv> -o <output_dir>
```
#### 3.3. Compute graphical soundscapes
Test configuration
```bash
python -m pamflow.graphical_soundscape.cli spectrogram_local_max -i <input_file>
```
Run for all files
```bash
python -m pamflow.graphical_soundscape.cli graphical_soundscape -i <input_metadata_csv> -o <output_dir>
```
Plot results
```bash
python -m pamflow.graphical_soundscape.cli plot_graph -i <input_dir>
```
#### 3.4. Compute BirdNet detections (optional)
To have additional information about bird communities, we recommend to use an external repository, namely [BirdNET-Analyzer](https://github.com/kahst/BirdNET-Analyzer). To do so, you will need to install BirdNet Dependencies and run the following scripts as per indicated in the repository. Here we provide some scripts that can be used. These will need to be adapted to your project needs.

```bash
python analyze.py --i <input_dir>  --o <output_dir> --lat <latitude_decimal> --lon <longitude_decimal> --threads 8 --rtype csv
```

```bash
python segments.py --audio <audio_folder> --results <detection_folder> --o <output_folder> --min_conf 0.8 --max_segments 10 --seg_length 5.0
```

### 4. Visualize and perform statistical analyses
Since the statistical analyses are project-dependent, specific visualization tools should be chosen to aid in the process.

## Directory Structure

The directory structure of projects is as follows:

```
project_folder
├── pamflow
│   ├── config.yaml
│   ├── preprocess
│   ├── acoustic_indices
│   └── graphical_soundscapes
├── input
│   ├── sensor_deployment.csv
│   └── mannot
├── output
│   ├── figures
│   ├── metadata
│   ├── dataframes_gs
│   └── dataframes_ai
├── README.md
└── requirements.txt
```

- `config.yaml`: configuration file for specifying input/output directories, settings, and parameters.
- `pamflow/`: directory containing scripts for loading data, feature extraction, data visualization, and statistical analysis.
- `input/`: directory containing input files comming from field data and manual annotations.
- `output/`: directory containing output files generated by the workflows.
- `README.md`: Adjust this file providing an overview of the project.
- `requirements.txt`: file listing all Python packages required to run the analisys.

## Contribution Guidelines

This project was developed with the intention of being openly available for anyone to use and improve it. If you wish to contribute to this project, please follow these steps:

1. Fork this repository to your own GitHub account.
2. Clone the forked repository to your local machine.
3. Create a new branch with a descriptive name for your contribution.
4. Make changes to the code or documentation.
5. Push your changes to your forked repository.
6. Create a pull request to the original repository.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
