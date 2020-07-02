#####################################################################
## plot multiscale wavelet variance
## create null bands by permuting the original data series
## generate plots and table of wavelet variance including p-values
#######################################################################
options(echo = FALSE)
library("wavethresh");
library("waveslim");
library("bitops");

## to determine if data is properly formatted 2^N observations
is_power2 <- function(x) {
    x && !(bitops::bitAnd(x, x - 1));
}

## dwt : discrete wavelet transform using Haar wavelet filter, simplest wavelet function but later can modify to let user-define the wavelet filter function
dwt_var_permut_get_max <- function(data, names, alpha, filter = 1, family = "DaubExPhase", bc = "symmetric", method = "kendall", wf = "haar", boundary = "reflection") {
    title <- NULL;
    final_pvalue <- NULL;
    j <- NULL;
    scale <- NULL;
    out <- NULL;

    print(class(data));
    print(names);
    print(alpha);

    par(mar = c(5, 4, 4, 3), oma = c(4, 4, 3, 2), xaxt = "s", cex = 1, las = 1);

    title <- c("Wavelet", "Variance", "Pvalue", "Test");
    print(title);

    for (i in seq_len(length(names))) {
        temp <- NULL;
        results <- NULL;
        wave1_dwt <- NULL;

        ## if data fails formatting check, do something
        print(is.numeric(as.matrix(data)[, i]));
        if (!is.numeric(as.matrix(data)[, i])) {
            stop("data must be a numeric vector");
        }
        print(length(as.matrix(data)[, i]));
        print(is_power2(length(as.matrix(data)[, i])));
        if (!is_power2(length(as.matrix(data)[, i]))) {
            stop("data length must be a power of two");
        }
        j <- wavethresh::wd(as.matrix(data)[, i], filter.number = filter, family = family, bc = bc)$nlevels;
        print(j);
        temp <- vector(length = j);
        wave1_dwt <- waveslim::dwt(as.matrix(data)[, i], wf = wf, j, boundary = boundary);

        temp <- waveslim::wave.variance(wave1_dwt)[- (j + 1), 1];
        print(temp);

        ##permutations code :
        feature1 <- NULL;
        null <- NULL;
        var_lower <- NULL;
        limit_lower <- NULL;
        var_upper <- NULL;
        limit_upper <- NULL;
        med <- NULL;

        limit_lower <- alpha / 2 * 1000;
        print(limit_lower);
        limit_upper <- (1 - alpha / 2) * 1000;
        print(limit_upper);

        feature1 <- as.matrix(data)[, i];
        for (k in 1:1000) {
            nk_1 <- NULL;
            null_levels <- NULL;
            var <- NULL;
            null_wave1 <- NULL;

            nk_1 <- sample(feature1, length(feature1), replace = FALSE);
            null_levels <- wavethresh::wd(nk_1, filter.number = filter, family = family, bc = bc)$nlevels;
            var <- vector(length = length(null_levels));
            null_wave1 <- waveslim::dwt(nk_1, wf = wf, j, boundary = boundary);
            var <- waveslim::wave.variance(null_wave1)[- (null_levels + 1), 1];
            null <- rbind(null, var);
        }
        null <- apply(null, 2, sort, na.last = TRUE);
        var_lower <- null[limit_lower, ];
        var_upper <- null[limit_upper, ];
        med <- (apply(null, 2, median, na.rm = TRUE));

        ## plot
        results <- cbind(temp, var_lower, var_upper);
        print(results);
        matplot(results, type = "b", pch = "*", lty = 1, col = c(1, 2, 2), xaxt = "n", xlab = "Wavelet Scale", ylab = "Wavelet variance");
        mtext(names[i], side = 3, line = 0.5, cex = 1);
        axis(1, at = 1:j, labels = c(2 ^ (0:(j - 1))), las = 3, cex.axis = 1);

        ## get pvalues by comparison to null distribution
        for (m in seq_len(length(temp))) {
            print(paste("scale", m, sep = " "));
            print(paste("var", temp[m], sep = " "));
            print(paste("med", med[m], sep = " "));
            pv <- NULL;
            tail <- NULL;
            scale <- NULL;
            scale <- 2 ^ (m - 1);
            if (temp[m] >= med[m]) {
                ## R tail test
                print("R");
                tail <- "R";
                pv <- (length(which(null[, m] >= temp[m]))) / (length(na.exclude(null[, m])));
            } else {
                if (temp[m] < med[m]) {
                    ## L tail test
                    print("L");
                    tail <- "L";
                    pv <- (length(which(null[, m] <= temp[m]))) / (length(na.exclude(null[, m])));
                }
            }
            print(pv);
            out <- rbind(out, c(paste("Scale", scale, sep = "_"), format(temp[m], digits = 3), pv, tail));
        }
        final_pvalue <- rbind(final_pvalue, out);
    }
    colnames(final_pvalue) <- title;
    return(final_pvalue);
}

## execute
## read in data
args <- commandArgs(trailingOnly = TRUE)

data_test <- NULL;
final <- NULL;
sub <- NULL;
sub_names <- NULL;
data_test <- read.delim(args[1], header = FALSE);
pdf(file = args[5], width = 11, height = 8)
for (f in strsplit(args[2], ",")) {
    f <- as.integer(f)
    if (f > ncol(data_test))
        stop(paste("column", f, "doesn't exist"));
    sub <- data_test[, f];
    sub_names <- colnames(data_test)[f];
    final <- rbind(final, dwt_var_permut_get_max(sub, sub_names, as.double(args[3])));
}

dev.off();
write.table(final, file = args[4], sep = "\t", quote = FALSE, row.names = FALSE);
