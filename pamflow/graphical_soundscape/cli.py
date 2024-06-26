""" Utilities to compute graphical soundscapes from audio files 

The functions here are a variant of the original graphical soundscapes introduced by Campos-Cerqueira et al. The peaks are detected on the spectrogram instead of detecting peaks on the spectrum. Results are similar but not equal to the ones computed using seewave in R.

References:
  - Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
  - Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
  - Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
"""
import os
import argparse
import pandas as pd
import glob
import matplotlib.pyplot as plt
from maad import sound, util
from maad.rois import spectrogram_local_max
from maad.features import graphical_soundscape, plot_graph
from pamflow.preprocess.utils import input_validation, load_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute graphical soundscape on audio data.")
    parser.add_argument(
        "operation", 
        choices=[
            "spectrogram_local_max",
            "graphical_soundscape",
            "plot_graph",
        ],
        help="Graphical soundscape operation")
    
    parser.add_argument("--input", "-i", type=str, 
                    help="Path to metadata or directory with audio files. "
                         "If providing a directory, all audio files in the directory will be processed.")
    parser.add_argument("--output", "-o", type=str,
                    help="Path and filename to save results. "
                         "Results will be saved to a file with the specified name at the specified location.")
    parser.add_argument("--config", "-c", type=str, default='config.yaml',
                    help="Path to config file. "
                         "The config file should contain all additional settings for your script.")
    parser.add_argument("--display", "-d", action="store_true", 
                    help="Enable to display plot")
    parser.add_argument( "--sites", "-s", nargs="+", default=None,
                    help="Specify sites to execute the operation (default: None)")
    args = parser.parse_args()
    
    # Load configuration
    config_file = args.config
    config = load_config(config_file)
    target_fs = config["graph_soundscapes"]["target_fs"]
    nperseg = config["graph_soundscapes"]["nperseg"]
    noverlap = config["graph_soundscapes"]["noverlap"]
    db_range = config["graph_soundscapes"]["db_range"]
    min_distance = config["graph_soundscapes"]["min_distance"]
    threshold_abs = config["graph_soundscapes"]["threshold_abs"]
    n_jobs = config["graph_soundscapes"]["n_jobs"]
    group_by_site = config["graph_soundscapes"]["group_by_site"]
    select_sites = args.sites

    # Operations
    if args.operation == "spectrogram_local_max":
        s, fs = sound.load(args.input)
        s = sound.resample(s, fs, target_fs, res_type="scipy_poly")
        Sxx, tn, fn, ext = sound.spectrogram(s, fs, nperseg=nperseg, noverlap=noverlap)
        Sxx_db = util.power2dB(Sxx, db_range=db_range)
        result = spectrogram_local_max(Sxx_db, tn, fn, ext, min_distance, 
                                       threshold_abs, display=True)
        plt.show()

    elif args.operation == "graphical_soundscape":
        df = input_validation(args.input)
        df['date'] = pd.to_datetime(df.date)
        df['time'] = df.date.dt.hour
        
        # If file list provided filter dataframe
        if select_sites is None:
            n_sites = df.groupby('sensor_name').ngroups
            site_list = df.sensor_name.unique()
        else:
            df = df[df['sensor_name'].isin(select_sites)]
            n_sites = df.groupby('sensor_name').ngroups
            site_list = df.sensor_name.unique()
        print(f'Computing graph over {n_sites} sites: {site_list}')

        # Group by site
        if group_by_site:  # saves results per site
            for site, df_site in df.groupby('sensor_name'):
                df_out = graphical_soundscape(
                    df_site, threshold_abs, 'path_audio', 'time', target_fs, nperseg, 
                    noverlap, db_range, min_distance, n_jobs)
                fname_save = os.path.join(args.output, f'{site}_graph.csv')
                df_out.to_csv(fname_save)
                print(f'{site} Done! Results are stored at {fname_save}')
        
        # Compute over all files
        else:
            df_out = graphical_soundscape(
                df, threshold_abs, 'path_audio', 'time', target_fs, nperseg, 
                noverlap, db_range, min_distance, n_jobs)
            df_out.to_csv(args.output, index=False)
            print(f'Done! Results are saved at {args.output}')
        
        # Display result
        if args.display:
            plot_graph(df_out)
            plt.show()
    
    elif args.operation == "plot_graph":
        print('Displaying plots from precomputed graphical soundscapes')

        if args.output is None:
            args.output = args.input
        
        flist = glob.glob(os.path.join(args.input,'*.csv'))
        for file in flist:
            file_basename = os.path.basename(file)
            fname_save = os.path.join(args.output, file_basename.replace('.csv', '.png'))
            graph = pd.read_csv(file, index_col=0)
            plot_graph(graph, savefig=True, fname=fname_save)
            plt.close()

        print(f'Done! Results are saved at {args.output}')
