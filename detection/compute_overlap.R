library(overlap)
# documentation: https://cran.r-project.org/web/packages/overlap/vignettes/overlap.pdf

# load data
sps = 'ATRPIL'
df = read.csv('../../output/detections/peptyr1_temporal_raw.csv')
df = df[c('Time', 'Sps', 'Zone')]

table(df$Zone)
range(df$Time)

timeRad <- df$Time * 2 * pi
sp_t0P <- timeRad[df$Zone == 't2_P']
sp_t0Z <- timeRad[df$Zone == 't2_Z']

# When less than 75 bservations, use Dhat1, otherwise use Dhat 4
min(length(sp_t0P), length(sp_t0Z))

ovlp <- overlapEst(sp_t0P, sp_t0Z, type="Dhat1")

overlapPlot(sp_t0P, sp_t0Z, adjust = 2, 
            main=paste(sps, "T0", "-", "∆hat", round(ovlp, 2)),
            xlab='Hora',
            ylab='Densidad')
legend('topright', c("Intervención", "Control"), lty=c(1,2), col=c(1,4), bty='n')



