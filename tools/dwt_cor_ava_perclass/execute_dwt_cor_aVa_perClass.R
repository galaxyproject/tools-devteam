##################################################################################
## code to do all correlation tests of form: motif(a) vs. motif(a)
## add code to create null bands by permuting the original data series
## generate plots and table matrix of correlation coefficients including p-values
##################################################################################
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

dwt_cor <- function(data_short, names_short, data_long, names_long, test, pdf, table, filter = 4, bc = "symmetric", method = "kendall", wf = "haar", boundary = "reflection") {
    print(test);
    print(pdf);
    print(table);

    pdf(file = pdf);
    final_pvalue <- NULL;
    title <- NULL;

    short_levels <- wavethresh::wd(data_short[, 1], filter.number = filter, bc = bc)$nlevels;
    title <- c("motif");
    for (i in 1:short_levels) {
        title <- c(title, paste(i, "cor", sep = "_"), paste(i, "pval", sep = "_"));
    }
    print(title);

    ## normalize the raw data
    data_short <- apply(data_short, 2, norm);
    data_long <- apply(data_long, 2, norm);

    for (i in seq_len(length(names_short))) {
        ## Kendall Tau
        ## DWT wavelet correlation function
        ## include significance to compare
        wave1_dwt <- NULL;
        wave2_dwt <- NULL;
        tau_dwt <- NULL;
        out <- NULL;

        print(names_short[i]);
        print(names_long[i]);

        ## need exit if not comparing motif(a) vs motif(a)
        if (names_short[i] != names_long[i]) {
            stop(paste("motif", names_short[i], "is not the same as", names_long[i], sep = " "));
        }
        else {
            wave1_dwt <- waveslim::dwt(data_short[, i], wf = wf, short_levels, boundary = boundary);
            wave2_dwt <- waveslim::dwt(data_long[, i], wf = wf, short_levels, boundary = boundary);
            tau_dwt <- vector(length = short_levels)

            ## perform cor test on wavelet coefficients per scale
            for (level in 1:short_levels) {
                w1_level <- NULL;
                w2_level <- NULL;
                w1_level <- (wave1_dwt[[level]]);
                w2_level <- (wave2_dwt[[level]]);
                tau_dwt[level] <- cor.test(w1_level, w2_level, method = method)$estimate;
            }

            ## CI bands by permutation of time series
            feature1 <- NULL;
            feature2 <- NULL;
            feature1 <- data_short[, i];
            feature2 <- data_long[, i];
            null <- NULL;
            results <- NULL;
            med <- NULL;
            cor_25 <- NULL;
            cor_975 <- NULL;

            for (k in 1:1000) {
                nk_1 <- NULL;
                nk_2 <- NULL;
                null_levels <- NULL;
                cor <- NULL;
                null_wave1 <- NULL;
                null_wave2 <- NULL;

                nk_1 <- sample(feature1, length(feature1), replace = FALSE);
                nk_2 <- sample(feature2, length(feature2), replace = FALSE);
                null_levels <- wavethresh::wd(nk_1, filter.number = filter, bc = bc)$nlevels;
                cor <- vector(length = null_levels);
                null_wave1 <- waveslim::dwt(nk_1, wf = wf, short_levels, boundary = boundary);
                null_wave2 <- waveslim::dwt(nk_2, wf = wf, short_levels, boundary = boundary);

                for (level in 1:null_levels) {
                    null_level1 <- NULL;
                    null_level2 <- NULL;
                    null_level1 <- (null_wave1[[level]]);
                    null_level2 <- (null_wave2[[level]]);
                    cor[level] <- cor.test(null_level1, null_level2, method = method)$estimate;
                }
                null <- rbind(null, cor);
            }

            null <- apply(null, 2, sort, na.last = TRUE);
            print(paste("NAs", length(which(is.na(null))), sep = " "));
            cor_25 <- null[25, ];
            cor_975 <- null[975, ];
            med <- (apply(null, 2, median, na.rm = TRUE));

            ## plot
            results <- cbind(tau_dwt, cor_25, cor_975);
            matplot(results, type = "b", pch = "*", lty = 1, col = c(1, 2, 2), ylim = c(-1, 1), xlab = "Wavelet Scale", ylab = "Wavelet Correlation Kendall's Tau", main = (paste(test, names_short[i], sep = " ")), cex.main = 0.75);
            abline(h = 0);

            ## get pvalues by comparison to null distribution
            ### modify pval calculation for error type II of T test ####
            out <- (names_short[i]);
            for (m in seq_len(length(tau_dwt))) {
                print(paste("scale", m, sep = " "));
                print(paste("tau", tau_dwt[m], sep = " "));
                print(paste("med", med[m], sep = " "));
                out <- c(out, format(tau_dwt[m], digits = 3));
                pv <- NULL;
                if (is.na(tau_dwt[m])) {
                    pv <- "NA";
                }
                else {
                    if (tau_dwt[m] >= med[m]) {
                        ## R tail test
                        print(paste("R"));
                        ### per sv ok to use inequality not strict
                        pv <- (length(which(null[, m] >= tau_dwt[m]))) / (length(na.exclude(null[, m])));
                        if (tau_dwt[m] == med[m]) {
                            print("tau == med");
                            print(summary(null[, m]));
                        }
                }
                    else if (tau_dwt[m] < med[m]) {
                        ## L tail test
                        print(paste("L"));
                        pv <- (length(which(null[, m] <= tau_dwt[m]))) / (length(na.exclude(null[, m])));
                    }
                }
                out <- c(out, pv);
                print(paste("pval", pv, sep = " "));
            }
            final_pvalue <- rbind(final_pvalue, out);
            print(out);
        }
    }
    colnames(final_pvalue) <- title;
    write.table(final_pvalue, file = table, sep = "\\t", quote = FALSE, row.names = FALSE)
    dev.off();
}
## execute
## read in data
args <- commandArgs(trailingOnly = TRUE)

input_data1 <- NULL;
input_data2 <- NULL;
input_data_short1 <- NULL;
input_data_short2 <- NULL;
input_data_names_short1 <- NULL;
input_data_names_short2 <- NULL;

input_data1 <- read.delim(args[1]);
input_data_short1 <- input_data1[, +c(seq_len(ncol(input_data1)))];
input_data_names_short1 <- colnames(input_data_short1);

input_data2 <- read.delim(args[2]);
input_data_short2 <- input_data2[, +c(seq_len(ncol(input_data2)))];
input_data_names_short2 <- colnames(input_data_short2);

## cor test for motif(a) in input_data1 vs motif(a) in input_data2
dwt_cor(input_data_short1, input_data_names_short1, input_data_short2, input_data_names_short2, test = "cor_aVa", pdf = args[3], table = args[4]);
print("done with the correlation test");
