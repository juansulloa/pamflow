# COMPUTE NMDS AND PLOT RESULT
library(vegan)
library(ade4)
library(RColorBrewer)
library(readxl)
library(dplyr)
path_gs = '../../../output/graphical_soundscapes/per_site-week/'
sites = list.files(path_gs, pattern='*.csv')

# load data and organize as a community matrix (sites as rows, soundscape component (species) as columns)
tf_bins = list()
for(site in sites){
  gs = read.csv(paste(path_gs,site,sep=''))
  sensor_name = strsplit(site, "_")[[1]][1]
  tf_bins[[sensor_name]] = as.vector(t(gs[,-1]))
}

# list to dataframe
tf_bins = as.data.frame(do.call(rbind, tf_bins))
sensor_names =  strsplit(row.names(tf_bins), "W", fixed = TRUE)
sensor_names = sapply(sensor_names, function(x) x[1])

# load environmental data
spatial_data = read_excel('../../../input/t1_sensor_deployment_spatial_variables.xlsx')

# Compute NMDS
tf_bins_nmds = metaMDS(tf_bins, distance = 'bray', trymax = 500)
stressplot(tf_bins_nmds)  # validate model fit
tf_bins_nmds$stress

# Plot results in 2D space
colors = RColorBrewer::brewer.pal(6, 'Dark2')
plt_data = as.data.frame(tf_bins_nmds$points)
plt_data['sensor_name'] = sensor_names
plt_data = left_join(plt_data, spatial_data, by = 'sensor_name')
plt_data['group'] = cut(plt_data$Percent_Tree, c(0,30,60,100), labels=c('Low', 'Mid', 'High'))

plot(plt_data[c('MDS1', 'MDS2')], col='gray', pch=16, bty='n',xlab='NMDS 1', ylab='NMDS 2', cex=0.5, cex.lab=1)
abline(v=0,col='gray',lty=2);abline(h=0,col='gray',lty=2)
s.class(plt_data[c('MDS1', 'MDS2')], fac=factor(plt_data$group), col = colors, add.plot = T)

plot(plt_data[c('MDS1', 'MDS2')], col='gray', pch=16, bty='n',xlab='NMDS 1', ylab='NMDS 2', cex=0.5, cex.lab=1)
abline(v=0,col='gray',lty=2);abline(h=0,col='gray',lty=2)
s.class(plt_data[c('MDS1', 'MDS2')], fac=factor(plt_data$sensor_name), 
        col = rep('gray', 200), add.plot = T)

