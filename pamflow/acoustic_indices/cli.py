""" Utility functions to use CLI for computing acoustic indices """

import os
import argparse
from pamflow.preprocess.utils import input_validation, load_config
from pamflow.acoustic_indices.utils import compute_indices

#%%
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Compute acoustic indices on audio data")
    parser.add_argument("--input", "-i", type=str, 
                    help="Path to metadata or directory with audio files. "
                         "If providing a directory, all audio files in the directory will be processed.")
    parser.add_argument("--output", "-o", type=str,
                    help="Path and filename to save results. "
                         "Results will be saved to a file with the specified name at the specified location.")
    parser.add_argument("--config", "-c", type=str, default='config.yaml',
                    help="Path to config file. "
                         "The config file should contain all additional settings for your script.")
    parser.add_argument( "--sites", "-s", nargs="+", default=None,
                    help="Specify sites to execute the operation (default: None)")
    args = parser.parse_args()

    # Load configuration
    df = input_validation(args.input)
    config_file = args.config
    config = load_config(config_file)
    target_fs = config["acoustic_indices"]["target_fs"]
    n_jobs = config["acoustic_indices"]["n_jobs"]
    group_by_site = config["acoustic_indices"]["group_by_site"]
    filter_type = config["acoustic_indices"]["filter_type"]
    filter_cut = config["acoustic_indices"]["filter_cut"]
    filter_order = config["acoustic_indices"]["filter_order"]
    select_sites = args.sites

    # If file list provided filter dataframe
    if select_sites is None:
        n_sites = df.groupby('sensor_name').ngroups
        site_list = df.sensor_name.unique()
    else:
        df = df[df['sensor_name'].isin(select_sites)]
        n_sites = df.groupby('sensor_name').ngroups
        site_list = df.sensor_name.unique()
    print(f'Computing indices over {n_sites} sites: {site_list}')

    # Format output per site or per batch
    if group_by_site:  
        for site, df_site in df.groupby('sensor_name'):
            df_out = compute_indices(
                df_site, target_fs, filter_type, filter_cut, filter_order, n_jobs)
            fname_save = os.path.join(args.output, f'{site}_indices.csv')
            df_out.to_csv(fname_save, index=False)
            print(f'{site} Done! Results are stored at {fname_save}')

    else:
        df_out = compute_indices(
            df, target_fs, filter_type, filter_cut, filter_order, n_jobs)
        df_out.to_csv(args.output, index=False)
        print(f'Done! Results are stored at {args.output}')
