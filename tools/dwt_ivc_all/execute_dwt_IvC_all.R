###########################################################################################
## code to do wavelet Indel vs. Control
## signal is the difference I-C; function is second moment i.e. variance from zero not mean
## to perform wavelet transf. of signal, scale-by-scale analysis of the function
## create null bands by permuting the original data series
## generate plots and table matrix of correlation coefficients including p-values
############################################################################################
library("wavethresh");
library("waveslim");

options(echo = FALSE)

## normalize data
norm <- function(data) {
    v <- (data - mean(data)) / sd(data);
    if (sum(is.na(v)) >= 1) {
        v <- data;
    }
    return(v);
}

dwt_cor <- function(data_short, names_short, data_long, names_long, test, pdf, table, filter = 4, bc = "symmetric", wf = "haar", boundary = "reflection") {
    print(test);
    print(pdf);
    print(table);

    pdf(file = pdf);
    final_pvalue <- NULL;
    title <- NULL;

    short_levels <- wavethresh::wd(data_short[, 1], filter.number = filter, bc = bc)$nlevels;
    title <- c("motif");
    for (i in 1:short_levels) {
        title <- c(title, paste(i, "moment2", sep = "_"), paste(i, "pval", sep = "_"), paste(i, "test", sep = "_"));
    }
    print(title);

    ## loop to compare a vs a
    for (i in seq_len(length(names_short))) {
        wave1_dwt <- NULL;
        m2_dwt <- NULL;
        diff <- NULL;
        var_dwt <- NULL;
        out <- NULL;
        out <- vector(length = length(title));

        print(names_short[i]);
        print(names_long[i]);

        ## need exit if not comparing motif(a) vs motif(a)
        if (names_short[i] != names_long[i]) {
            stop(paste("motif", names_short[i], "is not the same as", names_long[i], sep = " "));
        }
        else {
            ## signal is the difference I-C data sets
            diff <- data_short[, i] - data_long[, i];

            ## normalize the signal
            diff <- norm(diff);

            ## function is 2nd moment
            ## 2nd moment m_j = 1/N[sum_N(W_j + V_J)^2] = 1/N sum_N(W_j)^2 + (X_bar)^2
            wave1_dwt <- waveslim::dwt(diff, wf = wf, short_levels, boundary = boundary);
            var_dwt <- waveslim::wave.variance(wave1_dwt);
            m2_dwt <- vector(length = short_levels)
            for (level in 1:short_levels) {
                m2_dwt[level] <- var_dwt[level, 1] + (mean(diff)^2);
            }

            ## CI bands by permutation of time series
            feature1 <- NULL;
            feature2 <- NULL;
            feature1 <- data_short[, i];
            feature2 <- data_long[, i];
            null <- NULL;
            results <- NULL;
            med <- NULL;
            m2_25 <- NULL;
            m2_975 <- NULL;

            for (k in 1:1000) {
                nk_1 <- NULL;
                nk_2 <- NULL;
                m2_null <- NULL;
                var_null <- NULL;
                null_levels <- NULL;
                null_wave1 <- NULL;
                null_diff <- NULL;
                nk_1 <- sample(feature1, length(feature1), replace = FALSE);
                nk_2 <- sample(feature2, length(feature2), replace = FALSE);
                null_levels <- wavethresh::wd(nk_1, filter.number = filter, bc = bc)$nlevels;
                null_diff <- nk_1 - nk_2;
                null_diff <- norm(null_diff);
                null_wave1 <- waveslim::dwt(null_diff, wf = wf, short_levels, boundary = boundary);
                var_null <- waveslim::wave.variance(null_wave1);
                m2_null <- vector(length = null_levels);
                for (level in 1:null_levels) {
                    m2_null[level] <- var_null[level, 1] + (mean(null_diff)^2);
                }
                null <- rbind(null, m2_null);
            }

            null <- apply(null, 2, sort, na.last = TRUE);
            m2_25 <- null[25, ];
            m2_975 <- null[975, ];
            med <- apply(null, 2, median, na.rm = TRUE);

            ## plot
            results <- cbind(m2_dwt, m2_25, m2_975);
            matplot(results, type = "b", pch = "*", lty = 1, col = c(1, 2, 2), xlab = "Wavelet Scale", ylab = c("Wavelet 2nd Moment", test), main = (names_short[i]), cex.main = 0.75);
            abline(h = 1);

            ## get pvalues by comparison to null distribution
            out <- c(names_short[i]);
            for (m in seq_len(length(m2_dwt))) {
                print(paste("scale", m, sep = " "));
                print(paste("m2", m2_dwt[m], sep = " "));
                print(paste("median", med[m], sep = " "));
                out <- c(out, format(m2_dwt[m], digits = 4));
                pv <- NULL;
                if (is.na(m2_dwt[m])) {
                    pv <- "NA";
                }
                else {
                    if (m2_dwt[m] >= med[m]) {
                        ## R tail test
                        tail <- "R";
                        pv <- (length(which(null[, m] >= m2_dwt[m]))) / (length(na.exclude(null[, m])));
                    }
                    else{
                        if (m2_dwt[m] < med[m]) {
                            ## L tail test
                            tail <- "L";
                            pv <- (length(which(null[, m] <= m2_dwt[m]))) / (length(na.exclude(null[, m])));
                        }
                    }
                }
                out <- c(out, pv);
                print(pv);
                out <- c(out, tail);
            }
            final_pvalue <- rbind(final_pvalue, out);
            print(out);
        }
    }

    colnames(final_pvalue) <- title;
    write.table(final_pvalue, file = table, sep = "\t", quote = FALSE, row.names = FALSE);
    dev.off();
}
## execute
## read in data
args <- commandArgs(trailingOnly = TRUE)

input_data <- read.delim(args[1]);
input_data_names <- colnames(input_data);

control_data <- read.delim(args[2]);
control_data_names <- colnames(control_data);

## call the test function to implement IvC test
dwt_cor(input_data, input_data_names, control_data, control_data_names, test = "IvC", pdf = args[3], table = args[4]);
print("done with the correlation test");
