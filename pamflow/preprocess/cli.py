#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import argparse
from maad import util
from pamflow.preprocess.utils import (
    plot_sensor_deployment, 
    metadata_summary, 
    add_file_prefix, 
    audio_timelapse)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform preprocessing operations on audio data.")
    parser.add_argument(
        "operation", 
        choices=["get_audio_metadata", 
                 "metadata_summary",
                 "plot_sensor_deployment",
                 "audio_timelapse",
                 "add_file_prefix"], 
        help="Preprocessing operation")
    
    parser.add_argument("--input", "-i", 
                        type=str, help="Path to directory to search")
    parser.add_argument("--output", "-o", 
                        type=str, help="Path and filename to save results")
    parser.add_argument("--sample_length", "-sl", 
                        type=float, help="Sample length for audio timelapse")
    parser.add_argument("--date_ini", "-di",
                        type=str, help="Initial date for audio timelapse")
    parser.add_argument("--date_end", "-de",
                        type=str, help="End date for audio timelapse")
    parser.add_argument("--recursive", "-r", 
                        action="store_true", help="Enable recursive mode")
    parser.add_argument("--quiet", "-q", 
                        action="store_true", help="Enable quiet mode")
    args = parser.parse_args()
    
    verbose = 0 if args.quiet else 1

    if args.operation == "get_audio_metadata":
        df = util.get_metadata_dir(args.input, verbose)
        df.dropna(inplace=True)  # remove problematic files
        df.to_csv(args.output, index=False)
        plot_sensor_deployment(df)
        result = metadata_summary(df)
    
    elif args.operation == "add_file_prefix":
        result = add_file_prefix(args.input, args.recursive, verbose)
    
    elif args.operation == "plot_sensor_deployment":
        result = plot_sensor_deployment(args.input)
    
    elif args.operation == "audio_timelapse":
        date_range = [args.date_ini, args.date_end]
        result = audio_timelapse(
        args.input, args.sample_length, sample_period='30T', date_range=date_range, path_save=args.output, save_audio=True, verbose=True)
    
    elif args.operation == "metadata_summary":
        result = metadata_summary(args.input)

    print("\n")
    print(result)
