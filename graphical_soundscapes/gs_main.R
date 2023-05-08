## SOUNDSCAPE CHARACTERIZATION
# References
# Campos‐Cerqueira, M., et al., 2020. How does FSC forest certification affect the acoustically active fauna in Madre de Dios, Peru? Remote Sensing in Ecology and Conservation 6, 274–285. https://doi.org/10.1002/rse2.120
# Furumo, P.R., Aide, T.M., 2019. Using soundscapes to assess biodiversity in Neotropical oil palm landscapes. Landscape Ecology 34, 911–923.
# Campos-Cerqueira, M., Aide, T.M., 2017. Changes in the acoustic structure and composition along a tropical elevational gradient. JEA 1, 1–1. https://doi.org/10.22261/JEA.PNCO7I
source('gs_utils.R')
library(viridis)
library(vegan)
library(yaml)

## LOAD CONFIGURATION VARIABLES
config <- yaml.load_file('../config.yaml')
path_audio_dataset = config$input_data$path_audio  # location of audio dataset
path_save_gs = config$graph_soundscapes$path_save_gs  # location to save the dataframe
path_metadata = config$preprocessing$path_save_metadata_clean  # location to metadata information
path_save_fig = config$graph_soundscapes$path_save_fig  # location to save the figure

# 1. READ METADATA
df = read.csv(path_metadata)
df$path_audio = as.character(df$path_audio)
df$time = format(strptime(df$date, format = "%Y-%m-%d %H:%M:%S"), format = "%H:%M:%S")
sites = c('CAT001', 'CAT002', 'CAT009', 'CAT011')

## 2. REMOVE RAIN DATA
# This is an advanced feature and first requires the development of a rain detector

## 3. COMPUTE GRAPH SOUNDSCAPE FOR EACH RECORDING AND SAVE PLOT
for(site in sites){
    # set dataframe and compute graphical soundscape
    df_site = df[df$site==site,]
    df_site <- df_site[order(df_site$date), ]
    gs = graphical_soundscape(df_site, spec_wl=256, fpeaks_th=20, fpeaks_f=0, verbose=T)
    
    # save graph soundscape
    fname_save_gs = paste(path_save_gs, site, '.csv', sep='')
    write.csv(gs, file=fname_save_gs, row.names = F)
    
    # save fig
    fname_save_fig = paste(path_save_fig, site, '.png', sep='')
    png(fname_save_fig)
    plot_graphical_soundscape(gs)
    dev.off()
    }
