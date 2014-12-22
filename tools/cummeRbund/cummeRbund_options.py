from galaxy import eggs
eggs.require( 'SQLAlchemy' )
eggs.require( 'pysqlite>=2' )
from sqlalchemy import *
from sqlalchemy.sql import and_
from sqlalchemy import exceptions as sa_exceptions
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

def get_genes( database_path ):
    dburi = 'sqlite:///%s' % database_path
    engine = create_engine( dburi )
    meta = MetaData( bind=engine )
    db_session = Session = scoped_session( sessionmaker( bind=engine, autoflush=False, autocommit=True ) )
    gene_ids = db_session.execute( 'select gene_short_name, gene_id from genes order by gene_short_name' )
    return [ ( gene_id[ 0 ], gene_id[ 1 ], False ) for gene_id in gene_ids ]

def get_samples( database_path ):
    dburi = 'sqlite:///%s' % database_path
    engine = create_engine( dburi )
    meta = MetaData( bind=engine )
    db_session = Session = scoped_session( sessionmaker( bind=engine, autoflush=False, autocommit=True ) )
    samples = db_session.execute( 'select sample_name from samples order by sample_name' )
    return [ ( sample[ 0 ], sample[ 0 ], False ) for sample in samples ]
