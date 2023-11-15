# COMPUTE NMDS AND PLOT RESULT
library(vegan)
library(ade4)
library(RColorBrewer)
library(yaml)
library(readxl)
library(stringr)

## LOAD CONFIGURATION VARIABLES

# load data and organize as a community matrix (sites as rows, soundscape component (species) as columns)
df_species = read.csv('../../output/dataframes_mannot/proportions_species_all.csv')
df_codes = read_excel('../../input/mannot/sp_codes.xlsx', sheet='ALL_SP_CODES')

# Aggregate by day
site_idx = substr(df_species$fname, 1,2)
period_idx = substr(df_species$fname, 9,10)
period_idx = replace(period_idx, period_idx=='04', 't0')
period_idx = replace(period_idx, period_idx=='05', 't2')
period_idx = replace(period_idx, period_idx=='06', 't2')
site_period_idx = paste(site_idx, period_idx, sep = '_')
site_day = paste(site_idx, substr(df_species$fname, 9,13), sep='_')
df = aggregate(df_species, by = list(site_day), FUN = mean)

# Prepare data for NMDS
X = df[,4:108]
row.names(X) = df$Group.1
idx_group = paste(substr(df$Group.1, 1,2), substr(df$Group.1, 4,5), sep='_')
replacement_rules_noise <- c("P6_04" = "Alto", "P5_04" = "Alto", "P6_06" = "Bajo", "P5_06" = "Bajo", 
                              "Z5_04" = "Control", "Z6_04" = "Control", "Z5_06" = "Control", "Z6_05" = "Control")
replacement_rules_period <- c("P6_04" = "t0", "P5_04" = "t0", "P6_06" = "t2", "P5_06" = "t2", 
                             "Z5_04" = "t0", "Z6_04" = "t0", "Z5_06" = "t2", "Z6_05" = "t2")

idx_noise = str_replace_all(idx_group, replacement_rules_noise)
idx_period = str_replace_all(idx_group, replacement_rules_period)

# Compute NMDS
nmds_sp = metaMDS(X, distance = 'bray', trymax = 500)
stressplot(nmds_sp)  # validate model fit
nmds_sp$stress

# Plot results in 2D space
colors = RColorBrewer::brewer.pal(11, 'Paired')
plt_data = as.data.frame(nmds_sp$points)
plt_data['site'] = substr(row.names(plt_data), 1,2)
plt_data['period'] = idx_period
plt_data['ruido'] = idx_noise

plot(plt_data[c('MDS1', 'MDS2')], col='gray', pch=16, bty='n',xlab='NMDS 1', ylab='NMDS 2', cex=0.5, cex.lab=1, xlim=c(-1,1), ylim=c(-1,1))
abline(v=0,col='gray',lty=2);abline(h=0,col='gray',lty=2)
s.class(plt_data[c('MDS1', 'MDS2')], fac=factor(plt_data$ruido), col = colors, add.plot = T)
text(x=plt_data$MDS1, y=plt_data$MDS2, labels = plt_data$site, col = 'gray50', cex = 0.9)

# Save NMDS data
write.csv(plt_data, '../../output/dataframes_mannot/nmds_all_species_output.csv', row.names=FALSE)

# Use a non parametric test to evaluate significance of the groups
dist = vegdist(tf_bins, 'bray') # using 2D data
treatment = substr(row.names(tf_bins), 4,5)=='P6'
permanova = adonis2(dist~treatment, permutations = 1000)
permanova

## -- Find Indicator Bins -- ##
# Determine de groups
site_idx = substr(row.names(X), 1,2)
gp_idx = substr(row.names(X), 4,5)
gp_idx = replace(gp_idx, gp_idx=='04', 't0')
gp_idx = replace(gp_idx, gp_idx=='05', 't2')
gp_idx = replace(gp_idx, gp_idx=='06', 't2')
gp_idx = paste(site_idx, gp_idx, sep='_')
gp_idx = ifelse(grepl("P5_t0|P6_t0", vector), "Treatment", "Control")
gp_idx = factor(gp_idx)

# Compute indicator species index
library(labdsv)
iva = indval(X, as.numeric(gp_idx))

gr = iva$maxcls[iva$pval<=0.05]
gr = levels(gp_idx)[gr]
iv = iva$indcls[iva$pval<=0.05]
pv = iva$pval[iva$pval<=0.05]
fr = apply(X>0, 2, sum)[iva$pval<=0.05]
fidg = data.frame(group=gr, indval=iv, pvalue=pv, freq=fr)
fidg = fidg[order(fidg$group, -fidg$indval),]
fidg['species'] = row.names(fidg)
write.csv(fidg, '../../output/dataframes_mannot/indicator_species_results.csv', row.names = FALSE)
