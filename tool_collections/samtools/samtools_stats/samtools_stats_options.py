import pysam
import os
import tempfile
import shutil

def get_rg( bam_file_name ):

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

		ids = []

		for rg in bam_file.header['RG']:
			ids.append( rg['ID'] )

		bam_file.close()

		return [ ( id, id, False ) for id in ids ]

	except IOError as e:
		
		print "I/O error({0}): {1}".format( e.errno, e.strerror )

	finally:

		shutil.rmtree( temp_bam_dir )

	
