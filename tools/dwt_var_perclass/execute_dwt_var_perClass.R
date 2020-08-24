######################################################################
## plot power spectra, i.e. wavelet variance by class
## add code to create null bands by permuting the original data series
## get class of maximum significant variance per feature
## generate plots and table matrix of variance including p-values
######################################################################
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

dwt_var_permut_get_max <- function(data, names, outfile, filter = 4, bc = "symmetric", method = "kendall", wf = "haar", boundary = "reflection") {
    max_var <- NULL;
    matrix <- NULL;
    title <- NULL;
    final_pvalue <- NULL;
    short_levels <- NULL;
    scale <- NULL;

    print(names);

    par(mfcol = c(length(names), length(names)), mar = c(0, 0, 0, 0), oma = c(4, 3, 3, 2), xaxt = "s", cex = 1, las = 1);

    short_levels <- wavethresh::wd(data[, 1], filter.number = filter, bc = bc)$nlevels;

    title <- c("motif");
    for (i in seq_len(short_levels)) {
        title <- c(title, paste(i, "var", sep = "_"), paste(i, "pval", sep = "_"), paste(i, "test", sep = "_"));
    }
    print(title);

    ## normalize the raw data
    data <- apply(data, 2, norm);

    for (i in seq_len(length(names))) {
        for (j in seq_len(length(names))) {
            temp <- NULL;
            results <- NULL;
            wave1_dwt <- NULL;
            out <- NULL;

            out <- vector(length = length(title));
            temp <- vector(length = short_levels);

            if (i != j) {
                plot(temp, type = "n", axes = FALSE, xlab = NA, ylab = NA);
                box(col = "grey");
                grid(ny = 0, nx = NULL);
            } else {

                wave1_dwt <- waveslim::dwt(data[, i], wf = wf, short_levels, boundary = boundary);

                temp_row <- (short_levels + 1) * -1;
                temp_col <- 1;
                temp <- waveslim::wave.variance(wave1_dwt)[temp_row, temp_col];

                ##permutations code :
                feature1 <- NULL;
                null <- NULL;
                var_25 <- NULL;
                var_975 <- NULL;
                med <- NULL;

                feature1 <- data[, i];
                for (k in seq_len(1000)) {
                    nk_1 <- NULL;
                    null_levels <- NULL;
                    var <- NULL;
                    null_wave1 <- NULL;

                    nk_1 <- sample(feature1, length(feature1), replace = FALSE);
                    null_levels <- wavethresh::wd(nk_1, filter.number = filter, bc = bc)$nlevels;
                    var <- vector(length = length(null_levels));
                    null_wave1 <- waveslim::dwt(nk_1, wf = wf, short_levels, boundary = boundary);
                    var <- waveslim::wave.variance(null_wave1)[-8, 1];
                    null <- rbind(null, var);
                }
                null <- apply(null, 2, sort, na.last = TRUE);
                var_25 <- null[25, ];
                var_975 <- null[975, ];
                med <- (apply(null, 2, median, na.rm = TRUE));

                ## plot
                results <- cbind(temp, var_25, var_975);
                matplot(results, type = "b", pch = "*", lty = 1, col = c(1, 2, 2), axes = F);

                ## get pvalues by comparison to null distribution
                out <- (names[i]);
                for (m in seq_len(length(temp))) {
                    print(paste("scale", m, sep = " "));
                    print(paste("var", temp[m], sep = " "));
                    print(paste("med", med[m], sep = " "));
                    pv <- NULL;
                    tail <- NULL;
                    out <- c(out, format(temp[m], digits = 3));
                    if (temp[m] >= med[m]) {
                        ## R tail test
                        print("R");
                        tail <- "R";
                        pv <- (length(which(null[, m] >= temp[m]))) / (length(na.exclude(null[, m])));

                    } else {
                        ## L tail test
                        print("L");
                        tail <- "L";
                        pv <- (length(which(null[, m] <= temp[m]))) / (length(na.exclude(null[, m])));
                    }
                    out <- c(out, pv);
                    print(pv);
                    out <- c(out, tail);
                    ## get variances outside null bands by comparing temp to null
                    ### temp stores variance for each scale, and null stores permuted variances for null bands
                    if (temp[m] <= var_975[m]) {
                        temp[m] <- NA;
                    }
                }
                final_pvalue <- rbind(final_pvalue, out);
                matrix <- rbind(matrix, temp)
            }
            ## labels
            if (i == 1) {
                mtext(names[j], side = 2, line = 0.5, las = 3, cex = 0.25);
            }
            if (j == 1) {
                mtext(names[i], side = 3, line = 0.5, cex = 0.25);
            }
            if (j == length(names)) {
                axis(1, at = (1:short_levels), las = 3, cex.axis = 0.5);
            }
        }
    }
    colnames(final_pvalue) <- title;

    ## get maximum variance larger than expectation by comparison to null bands
    varnames <- vector();
    for (i in seq_len(length(names))) {
        name1 <- paste(names[i], "var", sep = "_")
        varnames <- c(varnames, name1)
    }
    rownames(matrix) <- varnames;
    colnames(matrix) <- (1:short_levels);
    max_var <- names;
    scale <- vector(length = length(names));
    for (x in seq_len(nrow(matrix))) {
        if (length(which.max(matrix[x, ])) == 0) {
            scale[x] <- NA;
        } else{
            scale[x] <- colnames(matrix)[which.max(matrix[x, ])];
        }
    }
    max_var <- cbind(max_var, scale);
    write.table(max_var, file = outfile, sep = "\t", quote = FALSE, row.names = FALSE, append = TRUE);
    return(final_pvalue);
}

## execute
## read in data
args <- commandArgs(trailingOnly = TRUE)

data_test <- NULL;
data_test <- read.delim(args[1]);

count <- ncol(data_test)
print(paste("The number of columns in the input file is: ", count));

# check if the number of motifs is not a multiple of 12, and round up is so
if (count %% 12 != 0) {
    print("the number of motifs is not a multiple of 12")
    count2 <- ceiling(count / 12);
}else{
    print("the number of motifs is a multiple of 12")
    count2 <- count / 12
}
print(paste("There will be", count2, "subfiles"))

pdf(file = args[4], width = 11, height = 8);

## loop to read and execute on all count2 subfiles
final <- NULL;
for (x in seq_len(count2)) {
    sub <- NULL;
    sub_names <- NULL;
    a <- NULL;
    b <- NULL;

    a <- ((x - 1) * 12 + 1);
    b <- x * 12;

    if (x < count2) {
        sub <- data_test[, +c(a:b)];
        sub_names <- colnames(data_test)[a:b];
        final <- rbind(final, dwt_var_permut_get_max(sub, sub_names, args[2]));
    }
    else{
        sub <- data_test[, +c(a:ncol(data_test))];
        sub_names <- colnames(data_test)[a:ncol(data_test)];
        final <- rbind(final, dwt_var_permut_get_max(sub, sub_names, args[2]));
    }
}

dev.off();

write.table(final, file = args[3], sep = "\t", quote = FALSE, row.names = FALSE);
