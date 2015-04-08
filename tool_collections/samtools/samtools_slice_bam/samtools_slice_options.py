import pysam
import os
import tempfile
import shutil

# This function below formats numbers with comma separators
# It is used to format length of reference sequences in return statement

def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


def get_references( bam_file_name ):

	try:

		temp_bam_dir = tempfile.mkdtemp()

		temp_bam_file = os.path.join( temp_bam_dir, "script_temp_input.bam" )
		temp_bai_file = os.path.join( temp_bam_dir, "script_temp_input.bam.bai" )

		# The symlinks below are necessary because pysam needs .bai file with the same base name as .bam file

		os.symlink( bam_file_name.file_name, temp_bam_file )
		os.symlink( bam_file_name.metadata.bam_index.file_name, temp_bai_file )

		# The version of pysam egg distributed with Galaxy is rather old
		# This is why pysam.Samfile is used
		# In latest version of pysam this is replaced with pysal.AlignmentFile 
		# However pysal.Samfile should still work in newer versions of pysam

		bam_file = pysam.Samfile( temp_bam_file  , "rb" )

		ref_names = bam_file.references
		ref_lengths = bam_file.lengths

		bam_file.close()

		return [ ( "%s (%s bp)" % ( ref_data[0], intWithCommas( int ( ref_data[1] ) ) ), ref_data[0], False ) for ref_data in zip(ref_names, ref_lengths) ]

	except IOError as e:
		
		print "I/O error({0}): {1}".format( e.errno, e.strerror )

	finally:

		shutil.rmtree( temp_bam_dir )

	
