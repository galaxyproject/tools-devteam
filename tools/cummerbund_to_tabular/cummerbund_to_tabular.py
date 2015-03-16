import os
import argparse
import sys
import string
import sqlite3

import logging


class CummerbundParser(object):

    def __init__(self, opts):
        self.cummerbund_db = opts.filename
        self.session = sqlite3.connect( os.path.abspath( self.cummerbund_db ) )

    def generate_file( self, table ):
        if hasattr( self, table ):
            with open( '%s.tabular' % table, 'w' ) as self.fh:
                getattr( self, table )()
        else:
            print 'Table %s is not supported or does not exist.' % table

    def __write_line(self, line):
        columns = []
        for col in line:
            if isinstance( col, float ):
                if str( col ) in [ '-inf', 'inf' ]:
                    columns.append( str( col ) )
                elif col == int(col):
                    columns.append( str( int( col ) ) )
                else:
                    columns.append( str( col ) )
            elif col is None:
                columns.append( '-' )
            else:
                columns.append( str( col ) )
        print >>self.fh, '\t'.join( columns )

    def __get_diff_from_table( self, table, identifier ):
        columns = [ '${table}.${identifier}', '${table}.gene_id', 'genes.gene_short_name', 'genes.locus',
                    '${table}.sample_1', '${table}.sample_2', '${table}.status',
                    '${table}.value_1', '${table}.value_2', '${table}.JS_dist',
                    '${table}.test_stat', '${table}.p_value', '${table}.q_value',
                    '${table}.significant' ]
        query = string.Template( 'SELECT %s FROM ${table} JOIN genes on ${table}.gene_id = genes.gene_id'  % ', '.join(columns) )
        result = self.session.execute( query.safe_substitute( table=table, identifier=identifier ) )
        self.__write_line( [ 'test_id', 'gene_id', 'gene', 'locus', 'sample_1', 
                             'sample_2', 'status', 'value_1', 'value_2', 'sqrt(JS)',
                             'test_stat', 'p_value', 'q_value', 'significant' ] )
        for row in result:
            self.__write_line( row )

    def __get_read_group_data( self, table, identifier ):
        header = [ 'tracking_id', 'condition', 'replicate', 'raw_frags',
                   'internal_scaled_frags', 'external_scaled_frags', 'FPKM',
                   'effective_length', 'status' ]
        columns = [ identifier, 'sample_name', 'replicate', 'raw_frags',
                    'internal_scaled_frags', 'external_scaled_frags', 'fpkm',
                    'effective_length', 'status' ]
        self.__write_line( header )
        for row in self.session.execute( 'SELECT %s FROM %s' % ( ', '.join( columns ), table ) ):
            self.__write_line( row )


    def __get_exp_diff( self, table, data_table, data_table_as, column ):
        header = [ 'test_id', 'gene_id', 'gene', 'locus', 'sample_1', 'sample_2',
                   'status', 'value_1', 'value_2', 'log2(fold_change)', 'test_stat',
                   'p_value', 'q_value', 'significant' ]
        columns = [ '${dtas}.${column}', '${table}.gene_id', '${table}.gene_short_name', '${table}.locus', 
                    '${dtas}.sample_1', '${dtas}.sample_2', '${dtas}.status',
                    '${dtas}.value_1', '${dtas}.value_2', '${dtas}.log2_fold_change',
                    '${dtas}.test_stat', '${dtas}.p_value', '${dtas}.q_value',
                    '${dtas}.significant' ]
        query = string.Template( 'SELECT %s FROM ${dtab} as ${dtas} JOIN ${table} on ${dtas}.${column} = ${table}.${column}' % ', '.join( columns )  )
        self.__write_line( header )
        for row in self.session.execute( query.safe_substitute( dtas=data_table_as, dtab=data_table, table=table, column=column ) ):
            self.__write_line( row )

    def __get_per_sample_fpkm( self, identifiers, table, column ):
        columns = []
        for identifier in identifiers:
            samples = self.session.execute( "SELECT sample_name FROM %s WHERE %s = '%s' ORDER BY sample_name ASC" % ( table, column, identifier[0] ) )
            for sample in samples:
                sample_name = sample[0]
                columns.extend( [ '%s_FPKM' % sample_name, 
                                  '%s_conf_lo' % sample_name,
                                  '%s_conf_hi' % sample_name, 
                                  '%s_status' % sample_name ] )
        return columns

    def __get_fpkms( self, table, data_table, column ):
        tss_columns = [ column, 'class_code', 'nearest_ref_id', 'gene_id',
                        'gene_short_name', column, 'locus', 'length', 'coverage' ]
        output_cols = [ 'tracking_id', 'class_code', 'nearest_ref_id', 'gene_id', 'gene_short_name',
                        'tss_id', 'locus', 'length', 'coverage' ]
        tss_groups = self.session.execute( 'SELECT %s FROM %s LIMIT 1'  % ( ', '.join( tss_columns ), table ) )
        output_cols.extend( self.__get_per_sample_fpkm( identifiers=tss_groups, column=column, table=data_table ) )
        self.__write_line( output_cols )
        tss_groups = self.session.execute( 'SELECT %s FROM %s' % ( ', '.join( tss_columns ), table ) )
        for tss_group in tss_groups:
            out_data = list( tss_group )
            samples = self.session.execute( "SELECT fpkm, conf_hi, conf_lo, quant_status FROM %s WHERE %s = '%s' ORDER BY sample_name ASC" % ( data_table, column, tss_group[0] ) )
            for sample in samples:
                out_data.extend( list( sample ) )
            self.__write_line( out_data )

    def __get_count_data( self, table, column ):
        output_cols = [ 'tracking_id' ]
        tss_groups = self.session.execute( 'SELECT %s FROM %s LIMIT 1' % ( column, table ) )
        output_cols.extend( self.__get_per_sample_count_cols( identifiers=tss_groups, table=table, column=column ) )
        self.__write_line( output_cols )
        self.__get_per_sample_count_data( table=table, column=column )

    def __get_per_sample_count_data( self, table, column ):
        result = self.session.execute( 'SELECT DISTINCT(%s) FROM %s' % ( column, table ) )
        for row in result:
            isoform_id = row[0]
            output_data = [ isoform_id ]
            per_sample = self.session.execute( "SELECT count, variance, uncertainty, dispersion, status FROM %s WHERE %s = '%s' ORDER BY sample_name ASC" % ( table, column, isoform_id ) )
            for samplerow in per_sample:
                output_data.extend( list( samplerow ) )
            self.__write_line( output_data )

    def __get_per_sample_count_cols( self, identifiers, table, column ):
        columns = []
        for identifier in identifiers:
            samples = self.session.execute( "SELECT sample_name FROM %s WHERE %s = '%s' ORDER BY sample_name ASC" % ( table, column, identifier[0] ) )
            for sample in samples:
                sample_name = sample[0]
                columns.extend( [ '%s_count' % sample_name, 
                                  '%s_count_variance' % sample_name,
                                  '%s_count_uncertainty_var' % sample_name, 
                                  '%s_count_dispersion_var' % sample_name,
                                  '%s_status' % sample_name ] )
        return columns

    def splicing_diff( self ):
        self.__get_diff_from_table( 'splicingDiffData', 'TSS_group_id' )

    def promoters_diff( self ):
        self.__get_diff_from_table( 'promoterDiffData', 'gene_id' )

    def cds_diff( self ):
        self.__get_diff_from_table( 'CDSDiffData', 'gene_id' )

    def tss_fpkm( self ):
        data_table = 'TSSData'
        table = 'TSS'
        column = 'TSS_group_id'
        self.__get_fpkms( data_table=data_table, table=table, column=column )

    def isoform_fpkm( self ):
        data_table = 'isoformData'
        table = 'isoforms'
        column = 'isoform_id'
        self.__get_fpkms( data_table=data_table, table=table, column=column )

    def genes_fpkm( self ):
        output_cols = [ 'tracking_id', 'class_code', 'nearest_ref_id', 'gene_id', 'gene_short_name',
                        'tss_id', 'locus', 'length', 'coverage' ]
        iso_groups = self.session.execute( 'SELECT gene_id FROM genes LIMIT 1' )
        output_cols.extend( self.__get_per_sample_fpkm( identifiers=iso_groups, column='gene_id', table='geneData' ) )
        self.__write_line( output_cols )
        data_columns = [ 'genes.gene_id', 'genes.class_code', 'genes.nearest_ref_id', 'genes.gene_id', 'genes.gene_short_name', 
                         'GROUP_CONCAT(TSS.TSS_group_id)', 'genes.locus', 'genes.length', 'genes.coverage' ]
        query = 'SELECT %s FROM genes JOIN TSS on TSS.gene_id = genes.gene_id GROUP BY genes.gene_id' % ', '.join( data_columns )
        result = self.session.execute( query )
        for row in result:
            gene_id = row[0]
            output_data = list( row )
            per_sample = self.session.execute( "SELECT fpkm, conf_lo, conf_hi, quant_status FROM geneData WHERE gene_id = '%s' ORDER BY sample_name ASC" % gene_id )
            for samplerow in per_sample:
                output_data.extend( list( samplerow ) )
            self.__write_line( output_data )

    def cds_fpkm( self ):
        output_cols = [ 'tracking_id', 'class_code', 'nearest_ref_id', 'gene_id', 'gene_short_name',
                        'tss_id', 'locus', 'length', 'coverage' ]
        iso_groups = self.session.execute( 'SELECT CDS_id FROM CDS LIMIT 1' )
        output_cols.extend( self.__get_per_sample_fpkm( identifiers=iso_groups, column='CDS_id', table='CDSData' ) )
        self.__write_line( output_cols )
        data_columns = [ 'CDS_id', 'class_code', 'nearest_ref_id', 'gene_id', 'gene_short_name', 
                         'GROUP_CONCAT(TSS_group_id)', 'locus', 'length', 'coverage' ]
        query = 'SELECT %s FROM CDS GROUP BY CDS_id' % ', '.join( data_columns )
        result = self.session.execute( query )
        for row in result:
            CDS_id = row[0]
            output_data = list( row )
            per_sample = self.session.execute( "SELECT fpkm, conf_lo, conf_hi, quant_status FROM CDSData WHERE CDS_id = '%s' ORDER BY sample_name ASC" % CDS_id )
            for samplerow in per_sample:
                output_data.extend( list( samplerow ) )
            self.__write_line( output_data )

    def tss_count_tracking( self ):
        self.__get_count_data( table='TSSCount', column='TSS_group_id' )

    def isoform_count( self ):
        self.__get_count_data( table='isoformCount', column='isoform_id' )

    def genes_count( self ):
        self.__get_count_data( table='geneCount', column='gene_id' )

    def cds_count( self ):
        self.__get_count_data( table='CDSCount', column='CDS_id' )

    def tss_group_exp( self ):
        columns = [ 'TEDD.TSS_group_id', 'TSS.gene_id', 'TSS.gene_short_name', 'TSS.locus',
                    'TEDD.sample_1', 'TEDD.sample_2', 'TEDD.status',
                    'TEDD.value_1', 'TEDD.value_2', 'TEDD.log2_fold_change',
                    'TEDD.test_stat', 'TEDD.p_value', 'TEDD.q_value', 'TEDD.significant' ]
        query = [ 'SELECT %s FROM TSSExpDiffData AS TEDD'  % ', '.join(columns),
                  'JOIN TSS on TEDD.TSS_group_id = TSS.TSS_group_id' ]
        self.__write_line( [ 'test_id', 'gene_id', 'gene', 'locus',
                             'sample_1', 'sample_2', 'status', 'value_1',
                             'value_2', 'log2(fold_change)', 'test_stat',
                             'p_value', 'q_value', 'significant' ] )
        for row in self.session.execute( ' '.join( query ) ):
            self.__write_line( row )

    def run_info( self ):
        self.__write_line( [ 'param', 'value' ] )
        for row in self.session.execute( 'SELECT param, value FROM runInfo' ):
            self.__write_line( row )

    def read_groups( self ):
        self.__write_line( [ 'file', 'condition', 'replicate_num', 'total_mass', 'norm_mass', 'internal_scale', 'external_scale' ] )
        for row in self.session.execute( 'SELECT file, sample_name, replicate, total_mass, norm_mass, internal_scale, external_scale FROM replicates' ):
            self.__write_line( row )

    def isoform_exp_diff( self ):
        self.__get_exp_diff( table='isoforms', data_table='isoformExpDiffData', data_table_as='iED', column='isoform_id' )

    def gene_exp_diff( self ):
        self.__get_exp_diff( table='genes', data_table='geneExpDiffData', data_table_as='gEDD', column='gene_id' )

    def cds_exp_diff( self ):
        self.__get_exp_diff( table='CDS', data_table='CDSExpDiffData', data_table_as='CED', column='CDS_id' )

    def tss_rg( self ):
        self.__get_read_group_data( table='TSSReplicateData', identifier='TSS_group_id' )

    def isoform_rg( self ):
        self.__get_read_group_data( table='isoformReplicateData', identifier='isoform_id' )

    def gene_rg( self ):
        self.__get_read_group_data( table='geneReplicateData', identifier='gene_id' )

    def cds_rg( self ):
        self.__get_read_group_data( table='CDSReplicateData', identifier='CDS_id' )

    def var_model( self ):
        header = [ 'condition', 'locus', 'compatible_count_mean', 'compatible_count_var', 'total_count_mean', 'total_count_var', 'fitted_var' ]
        self.__write_line( header )
        for row in self.session.execute( 'SELECT %s FROM varModel' % ', '.join( header ) ):
            self.__write_line( row )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( '--file', dest='filename' )
    parser.add_argument( '--tables', dest='tables', action='append' )
    opts = parser.parse_args()
    cb = CummerbundParser( opts )
    for table in opts.tables:
        cb.generate_file( table )
