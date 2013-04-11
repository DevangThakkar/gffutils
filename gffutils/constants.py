
SCHEMA = """

CREATE TABLE features (
    id text,
    seqid text,
    source text,
    featuretype text,
    start int,
    end int,
    score float,
    strand text,
    frame text,
    attributes text,
    extra text,
    bin int,
    primary key (id)
    );

CREATE TABLE relations (
    parent text,
    child text,
    level int,
    primary key (parent, child, level)
    );

CREATE TABLE meta (
    dialect text,
    version text
    );

CREATE TABLE directives (
    directive text
    );

CREATE TABLE autoincrements (
    base text,
    n int,
    primary key (base)
    );

"""

_keys = ['id', 'seqid', 'source', 'featuretype', 'start', 'end', 'score',
         'strand', 'frame', 'attributes', 'extra', 'bin']
_gffkeys = ['seqid', 'source', 'featuretype', 'start', 'end', 'score', 'strand',
            'frame', 'attributes']
_gffkeys_extra = _gffkeys + ['extra']

_SELECT = "SELECT " + ', '.join(_keys) + " FROM features "
_INSERT = "INSERT INTO features (" \
    + ', '.join(_keys) + ") VALUES (" + ','.join(list('?' * len(_keys))) + ")"


# TODO: create indexes once profiling figures out which ones work best....
INDEXES = []


# This dictionary keeps track of idiosyncracies to [attempt to] maintain
# invariance of file->db->file round trips.
dialect = {

    # Initial semicolon, e.g.,
    #
    #   ;ID=001;
    # vs
    #   ID=001;
    'leading semicolon': False,

    # Semicolon after the last value, e.g.,
    #
    #   ID=001; Name=gene1;
    # vs
    #   ID=001; Name=gene1
    'trailing semicolon': False,

    # e.g.,
    #
    #   gene_id "GENE1"
    # vs
    #   gene_id GENE1
    'quoted GFF2 values': False,

    # Sometimes there's extra space surrounding the semicolon, e.g.,
    #
    #   ID=001;Name=gene1
    # vs
    #   ID=001; Name=gene1
    'field separator': ';',

    # Usually "=" for GFF3; " " for GTF, e.g.,
    #
    #   gene_id "GENE1"
    # vs
    #   gene_id="GENE1"
    'keyval separator': '=',

    # Usually a comma, e.g.,
    #
    #   Parent=gene1,gene2,gene3
    'multival separator': ',',

    # General GTF or GFF format
    'fmt': 'gff3',

    # How multiple values for the same key are handled, e.g.,
    #
    #   Parent=gene1; Parent=gene2;
    # vs
    #   Parent=gene1,gene2;
    #
    # (the first one has repeated keys)
    'repeated keys': False,
}