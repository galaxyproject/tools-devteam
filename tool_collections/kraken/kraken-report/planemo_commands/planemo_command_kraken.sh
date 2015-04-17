planemo tool_init --force --id "kraken" --name "Classify with kraken" \
			--requirement Kraken@0.10.3-beta \
			--example_command 'kraken --db $DBNAME seqs.fa > classified_seqs.txt' \
			--example_input seqs.fa  \
			--example_output classified_seqs.txt \
			--test_case \
			--help_from_command 'kraken --help'