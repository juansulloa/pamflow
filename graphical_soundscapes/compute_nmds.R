# COMPUTE NMDS AND PLOT RESULT
library(vegan)
library(ade4)
library(RColorBrewer)
library(yaml)

## LOAD CONFIGURATION VARIABLES
config <- yaml.load_file('../config.yaml')
path_gs = config$graph_soundscapes$path_save_gs  # location to save the dataframe
path_gs = "../../output/dataframes_gs/python_gs/"
sites = list.files(path_gs, pattern='*.csv')

# load data and organize as a community matrix (sites as rows, soundscape component (species) as columns)
tf_bins = list()
for(site in sites){
  gs = read.csv(paste(path_gs,site,sep=''))
  gs = gs[,13:129] # remove hour column and 18 columns with frequency peaks below 2 kHz.
  sensor_name = substr(site, 1, 10)
  tf_bins[[sensor_name]] = as.vector(t(gs[,-1]))
}

# list to dataframe
tf_bins = as.data.frame(do.call(rbind, tf_bins))

# remove outliers
rm_rows = c('t0_P3-G035', 't1_P3-G035', 't2_P3-G035', 't0_P4-G033', 't1_P4-G033', 't2_P4-G033')
tf_bins = tf_bins[!is.element(row.names(tf_bins), rm_rows),]

# Compute NMDS
tf_bins_nmds = metaMDS(tf_bins, distance = 'bray', trymax = 500)
stressplot(tf_bins_nmds)  # validate model fit
tf_bins_nmds$stress

# Plot results in 2D space
colors = RColorBrewer::brewer.pal(11, 'Paired')
plt_data = as.data.frame(tf_bins_nmds$points)
plt_data['period'] = substr(row.names(plt_data), 1, 2)
plt_data['site'] = substr(row.names(plt_data), 4, 5)

plot(plt_data[c('MDS1', 'MDS2')], col='gray', pch=16, bty='n',xlab='NMDS 1', ylab='NMDS 2', cex=0.5, cex.lab=1, xlim=c(-1,1), ylim=c(-1,1))
abline(v=0,col='gray',lty=2);abline(h=0,col='gray',lty=2)
s.class(plt_data[c('MDS1', 'MDS2')], fac=factor(plt_data$site), col = colors, add.plot = T)
text(x=plt_data$MDS1, y=plt_data$MDS2, labels = plt_data$period, col = 'gray50')

# Save NMDS data
xdata = data.frame(NMDS1=tf_bins_nmds$points[,1], NMDS2=tf_bins_nmds$points[,2], 
                   Cobertura=factor(plt_data$Cobertura))
xdata['sensor_name'] = substr(row.names(xdata), 1, 4)
write.csv(xdata, './nmds_data/nmds_data.csv', row.names=FALSE)

# Use a non parametric test to evaluate significance of the groups
dist = vegdist(tf_bins, 'bray') # using 2D data
treatment = substr(row.names(tf_bins), 4,5)=='P6'
permanova = adonis2(dist~treatment, permutations = 1000)
permanova

## -- Find Indicator Bins -- ##
# combine data frames with environmental data
tf_bins_df = as.data.frame(tf_bins_nmds$points)
tf_bins_df['sensor_name'] = substr(row.names(tf_bins_df), 1, 4) 
tf_bins_df = merge(tf_bins_df, env, by.x = 'sensor_name', by.y='sensor_name')
tf_bins_presence = tf_bins[,colSums(tf_bins)>0]  # select only columns with no zeros

# Determine de groups
cover = tf_bins_df$Cobertura
idx_keep = is.element(cover, c('Bosque Ripario', 'Herbazales', 'Palma'))
tf_bins_presence = tf_bins_presence[idx_keep,]
cover = factor(cover[idx_keep])

# Compute indicator species index
library(labdsv)
iva = indval(tf_bins_presence, as.numeric(cover))

gr = iva$maxcls[iva$pval<=0.05]
gr = levels(cover)[gr]
iv = iva$indcls[iva$pval<=0.05]
pv = iva$pval[iva$pval<=0.05]
fr = apply(tf_bins_presence>0, 2, sum)[iva$pval<=0.05]
fidg = data.frame(group=gr, indval=iv, pvalue=pv, freq=fr)
fidg = fidg[order(fidg$group, -fidg$indval),]
fidg['tf_bin'] = row.names(fidg)
write.csv(fidg, './indicator_species_data/indval.csv', row.names = FALSE)

# Compute measures of mean dispersion for each cover
# NOTE: Check python script to compute values for each observation and evaluate statistically.
dispersion = data.frame('Cobertura' = unique(xdata$Cobertura), 'value'=vector(length=6))
for(cobertura in unique(xdata$Cobertura)){
  df_cover = xdata[xdata$Cobertura==cobertura,]
  centroid = data.frame('NMDS1'= mean(df_cover$NMDS1), 
                        'NMDS2'= mean(df_cover$NMDS2),
                        'Cobertura' = 'centroid',
                        'sensor_name'='centroid',
                        row.names='centroid')
  df_cover = rbind(df_cover, centroid)
  dist = vegdist(df_cover[c('NMDS1', 'NMDS2')], 'euclidean')
  dist = as.matrix(dist)
  dispersion_cover = mean(dist[nrow(dist),1:nrow(dist)-1])
  dispersion[dispersion$Cobertura==cobertura, 'value'] = dispersion_cover
  }