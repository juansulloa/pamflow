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

The Python programming language has become key for analyzing soundscapes since it is an open-source language and provides numerous scientific libraries for manipulating sound data. This project provides a template for organizing sound data analysis code and provides an example of how to analyze sound recordings in the .wav format.

## Installation Instructions

To get started with this project, you will need to clone this repository:

```bash
git clone https://github.com/juansulloa/soundscape_analysis_template.git
```

Then, install the required packages by running:

```bash
pip install -r requirements.txt
```

## Getting Started

To use this project, follow these general steps:

1. Organize directories
    - Sound files must be organized into subdirectories based on the recording device.
    - Rename the dorectory where you have this repository as 'workflows'.
    - Create the output directory and its subdirectories 'figures' and 'metadata'.
2. Edit the `config.yaml` file in the root directory to point to your sound files and adjust the settings according to your analysis needs.
3. Run the Jupyter notebooks in the `notebooks/` directory to extract features from your sound files and visualize the results. 

The Jupyter notebooks include detailed explanations of each step in the analysis process, including loading sound data, feature extraction, data visualization, and statistical analysis.

## Directory Structure

The directory structure of this project is as follows:

```
├── data
│   ├── SITE001
│   │   ├── recording1.wav
│   │   └── recording2.wav
│   ├── SITE002
│   │   └── recording3.wav
│   └── SITE003
│       └── recording4.wav
├── workflows
│   ├── config.yaml
│   ├── preprocessing
│   ├── acoustic_indices
│   └── graphical_soundscapes
├── output
│   ├── figures
│   ├── metadata
│   ├── dataframes_gs
│   └── dataframes_ai
├── README.md
└── requirements.txt
```

- `config.yaml`: configuration file for specifying input/output directories, settings, and parameters.
- `data/`: directory containing sound files organized into subdirectories based on location or device.
- `workflows/`: directory containing scripts for loading data, feature extraction, data visualization, and statistical analysis.
- `output/`: directory containing output files generated by the workflows.
- `README.md`: this file providing an overview of the project.
- `requirements.txt`: file listing all Python packages required to run the notebooks.

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
