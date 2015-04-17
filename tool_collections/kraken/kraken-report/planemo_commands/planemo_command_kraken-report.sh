planemo tool_init --force --id "kraken-report" --name "View a sample report of your classification" --requirement Kraken@0.10.3-beta --example_command 'kraken-report --db $DBNAME sequences.kraken > sequences.report' --example_input sequences.kraken --example_output sequences.report --help_text 'The output of kraken-report is tab-delimited, with one line per taxon. The fields of the output, from left-to-right, are as follows:

1)Percentage of reads covered by the clade rooted at this taxon

2)Number of reads covered by the clade rooted at this taxon

3)Number of reads assigned directly to this taxon

4)A rank code, indicating (U)nclassified, (D)omain, (K)ingdom, (P)hylum, (C)lass, (O)rder, (F)amily, (G)enus, or (S)pecies. All other ranks are simply '-'.

5)NCBI taxonomy ID

6)indented scientific name'