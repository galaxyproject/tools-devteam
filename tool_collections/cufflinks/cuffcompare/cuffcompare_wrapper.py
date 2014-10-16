#!/usr/bin/env python

# Supports Cuffcompare versions v1.3.0 and newer.

import optparse, os, shutil, subprocess, sys, tempfile

def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def __main__():
    #Parse Command Line
    parser = optparse.OptionParser()
    parser.add_option( '-r', dest='ref_annotation', help='An optional "reference" annotation GTF. Each sample is matched against this file, and sample isoforms are tagged as overlapping, matching, or novel where appropriate. See the refmap and tmap output file descriptions below.' )
    parser.add_option( '-R', action="store_true", dest='ignore_nonoverlap_reference', help='If -r was specified, this option causes cuffcompare to ignore reference transcripts that are not overlapped by any transcript in one of cuff1.gtf,...,cuffN.gtf. Useful for ignoring annotated transcripts that are not present in your RNA-Seq samples and thus adjusting the "sensitivity" calculation in the accuracy report written in the transcripts accuracy file' )
    parser.add_option( '-Q', action="store_true", dest='ignore_nonoverlap_transfrag', help='If -r was specified, this option causes cuffcompare to consider only the input transcripts that overlap any of the reference transcripts (Sp correction); Warning: this will discard all "novel" loci!)' )

    parser.add_option( '-s', dest='use_seq_data', action="store_true", help='Causes cuffcompare to look into for fasta files with the underlying genomic sequences (one file per contig) against which your reads were aligned for some optional classification functions. For example, Cufflinks transcripts consisting mostly of lower-case bases are classified as repeats. Note that <seq_dir> must contain one fasta file per reference chromosome, and each file must be named after the chromosome, and have a .fa or .fasta extension.')
    
    parser.add_option( '-M', action="store_true", dest='discard_single_exon_all', help='discard (ignore) single-exon transfrags and reference transcript')
    parser.add_option( '-N', action="store_true", dest='discard_single_exon_ref', help='discard (ignore) single-exon reference transcripts')
    parser.add_option( '-e', dest='max_dist_exon', help='Max. Distance for assessing exon accuracy" help="max. distance (range) allowed from free ends of terminal exons of reference transcripts when assessing exon accuracy. Default: 100')
    parser.add_option( '-d', dest='max_dist_group', help='Max.Distance for transcript grouping" help="max. distance (range) for grouping transcript start sites. Default: 100')
    parser.add_option( '-F', action="store_true", dest='discard_redundant_intron_transfrags', help='Discard intron-redundant transfrags if they share the 5-prime end (if they differ only at the 3-prime end)')

    # Wrapper / Galaxy options.
    parser.add_option( '', '--index', dest='index', help='The path of the reference genome' )
    parser.add_option( '', '--ref_file', dest='ref_file', help='The reference dataset from the history' )
    
    # Outputs.
    parser.add_option( '', '--combined-transcripts', dest='combined_transcripts' )
    
    (options, args) = parser.parse_args()
    
    # output version # of tool
    try:
        tmp = tempfile.NamedTemporaryFile().name
        tmp_stdout = open( tmp, 'wb' )
        proc = subprocess.Popen( args='cuffcompare 2>&1', shell=True, stdout=tmp_stdout )
        tmp_stdout.close()
        returncode = proc.wait()
        stdout = None
        for line in open( tmp_stdout.name, 'rb' ):
            if line.lower().find( 'cuffcompare v' ) >= 0:
                stdout = line.strip()
                break
        if stdout:
            sys.stdout.write( '%s\n' % stdout )
        else:
            raise Exception
    except:
        sys.stdout.write( 'Could not determine Cuffcompare version\n' )
        
    # Set/link to sequence file.
    if options.use_seq_data:
        if options.ref_file:
            # Sequence data from history.
            # Create symbolic link to ref_file so that index will be created in working directory.
            seq_path = "ref.fa"
            os.symlink( options.ref_file, seq_path  )
        else:
            if not os.path.exists( options.index ):
                stop_err( 'Reference genome %s not present, request it by reporting this error.' % options.index )
            seq_path = options.index
    
    # Build command.
    
    # Base.
    cmd = "cuffcompare -o cc_output "
    
    # Add options.
    if options.ref_annotation:
        cmd += " -r %s " % options.ref_annotation
    if options.ignore_nonoverlap_reference:
        cmd += " -R "
    if options.ignore_nonoverlap_transfrag:
	cmd += " -Q "
    if options.use_seq_data:
        cmd += " -s %s " % seq_path
    if options.discard_single_exon_all:
	cmd += " -M "
    if options.discard_single_exon_ref:
	cmd += " -N "
    if options.max_dist_exon:
	cmd += " -e %i " % int( options.max_dist_exon )
    if options.max_dist_group:
	cmd += " -d %i " % int( options.max_dist_group )
    if options.discard_redundant_intron_transfrags: 
	cmd += " -F "
    # Add input files.
        
    # Need to symlink inputs so that output files are written to temp directory.
    for i, arg in enumerate( args ):
        input_file_name = "./input%i" % ( i+1 )
        os.symlink( arg, input_file_name )
        cmd += "%s " % input_file_name

    # Debugging.
    print cmd
    
    # Run command.
    try:        
        tmp_name = tempfile.NamedTemporaryFile( dir="." ).name
        tmp_stderr = open( tmp_name, 'wb' )
        proc = subprocess.Popen( args=cmd, shell=True, stderr=tmp_stderr.fileno() )
        returncode = proc.wait()
        tmp_stderr.close()
        
        # Get stderr, allowing for case where it's very large.
        tmp_stderr = open( tmp_name, 'rb' )
        stderr = ''
        buffsize = 1048576
        try:
            while True:
                stderr += tmp_stderr.read( buffsize )
                if not stderr or len( stderr ) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stderr.close()
        
        # Error checking.
        if returncode != 0:
            raise Exception, stderr
            
        # Copy outputs.
        shutil.copyfile( "cc_output.combined.gtf" , options.combined_transcripts )    
            
        # check that there are results in the output file
        cc_output_fname = "cc_output.stats"
        if len( open( cc_output_fname, 'rb' ).read().strip() ) == 0:
            raise Exception, 'The main output file is empty, there may be an error with your input file or settings.'
    except Exception, e:
        stop_err( 'Error running cuffcompare. ' + str( e ) )
        
if __name__=="__main__": __main__()
