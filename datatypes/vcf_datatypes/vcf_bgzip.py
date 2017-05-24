"""
Binary classes
"""

import binascii
import gzip
import logging
import os
import shutil
import struct
import subprocess
import tempfile
import re
import warnings
import zipfile

from galaxy.datatypes.metadata import MetadataElement, MetadataParameter, ListParameter, DictParameter
from galaxy.datatypes import metadata
from galaxy.datatypes import dataproviders
from galaxy.datatypes.tabular import Tabular
from galaxy.datatypes.binary import Binary

log = logging.getLogger(__name__)


class VcfBgzip( Vcf ):
    """Class describing a VCF-BGZip file"""
    edam_format = "format_3020"
    file_ext = "bcf"

    MetadataElement( name="bcf_index", desc="BCF Index File", param=metadata.FileParameter, file_ext="csi", readonly=True, no_value=None, visible=False, optional=True )

    def sniff( self, filename ):
        # VCF-BGZip is compressed in the BGZF format, and must not be uncompressed in Galaxy.
        # The first line of any vcf file describes the VCF format.
        try:
            header = gzip.open( filename ).read(16)
            if binascii.b2a_hex( header ) == binascii.hexlify( '##fileformat=VCF' ):
                return True
            return False
        except:
            return False

    def set_meta( self, dataset, overwrite = True, **kwd ):
        """ Creates the index for the VCF-BGZip file. """
        # These metadata values are not accessible by users, always overwrite
        index_file = dataset.metadata.bcf_index
        if not index_file:
            index_file = dataset.metadata.spec['bcf_index'].param.new_file( dataset = dataset )
        # Create the bcf index
        ##$ bcftools index
        ##Usage: bcftools index <in.vcf.gz>

        dataset_symlink = os.path.join( os.path.dirname( index_file.file_name ),
                    '__dataset_%d_%s' % ( dataset.id, os.path.basename( index_file.file_name ) ) )
        os.symlink( dataset.file_name, dataset_symlink )

        stderr_name = tempfile.NamedTemporaryFile( prefix = "vcf_index_stderr" ).name
        command = [ 'bcftools', 'index', dataset_symlink ]
        proc = subprocess.Popen( args=command, stderr=open( stderr_name, 'wb' ) )
        exit_code = proc.wait()
        shutil.move( dataset_symlink + '.csi', index_file.file_name )

        stderr = open( stderr_name ).read().strip()
        if stderr:
            if exit_code != 0:
                os.unlink( stderr_name ) #clean up
                raise Exception, "Error Setting BCF Metadata: %s" % stderr
            else:
                print stderr
        dataset.metadata.bcf_index = index_file
        # Remove temp file
        os.unlink( stderr_name )

Binary.register_sniffable_binary_format("vcf_bgzip", "vcf_bgzip", VcfBgzip)
