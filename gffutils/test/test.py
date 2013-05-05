import gffutils
import gffutils.helpers as helpers
import sys
import os
import sqlite3
import nose.tools as nt
import difflib
import pprint
import copy


testdbfn_gtf = 'testing.gtf.db'
testdbfn_gff = 'testing.gff.db'

if os.path.exists(testdbfn_gtf):
    os.unlink(testdbfn_gtf)
if os.path.exists(testdbfn_gff):
    os.unlink(testdbfn_gff)

def setup():
    gffutils.create_db(gffutils.example_filename('FBgn0031208.gff'), testdbfn_gff, verbose=False, force=True)
    gffutils.create_db(gffutils.example_filename('FBgn0031208.gtf'), testdbfn_gtf, verbose=False, force=True)




def EXPECTED_DATA():
    # list the children and their expected first-order parents for the GFF test file.
    GFF_parent_check_level_1 = {'FBtr0300690':['FBgn0031208'],
                                'FBtr0300689':['FBgn0031208'],
                                'CG11023:1':['FBtr0300689','FBtr0300690'],
                                'five_prime_UTR_FBgn0031208:1_737':['FBtr0300689','FBtr0300690'],
                                'CDS_FBgn0031208:1_737':['FBtr0300689','FBtr0300690'],
                                'intron_FBgn0031208:1_FBgn0031208:2':['FBtr0300690'],
                                'intron_FBgn0031208:1_FBgn0031208:3':['FBtr0300689'],
                                'FBgn0031208:3':['FBtr0300689'],
                                'CDS_FBgn0031208:3_737':['FBtr0300689'],
                                'CDS_FBgn0031208:2_737':['FBtr0300690'],
                                'exon:chr2L:8193-8589:+':['FBtr0300690'],
                                'intron_FBgn0031208:2_FBgn0031208:4':['FBtr0300690'],
                                'three_prime_UTR_FBgn0031208:3_737':['FBtr0300689'],
                                'FBgn0031208:4':['FBtr0300690'],
                                'CDS_FBgn0031208:4_737':['FBtr0300690'],
                                'three_prime_UTR_FBgn0031208:4_737':['FBtr0300690'],
                               }

    # and second-level . . . they should all be grandparents of the same gene.
    GFF_parent_check_level_2 = {
                                'CG11023:1':['FBgn0031208'],
                                'five_prime_UTR_FBgn0031208:1_737':['FBgn0031208'],
                                'CDS_FBgn0031208:1_737':['FBgn0031208'],
                                'intron_FBgn0031208:1_FBgn0031208:2':['FBgn0031208'],
                                'intron_FBgn0031208:1_FBgn0031208:3':['FBgn0031208'],
                                'FBgn0031208:3':['FBgn0031208'],
                                'CDS_FBgn0031208:3_737':['FBgn0031208'],
                                'CDS_FBgn0031208:2_737':['FBgn0031208'],
                                'FBgn0031208:2':['FBgn0031208'],
                                'intron_FBgn0031208:2_FBgn0031208:4':['FBgn0031208'],
                                'three_prime_UTR_FBgn0031208:3_737':['FBgn0031208'],
                                'FBgn0031208:4':['FBgn0031208'],
                                'CDS_FBgn0031208:4_737':['FBgn0031208'],
                                'three_prime_UTR_FBgn0031208:4_737':['FBgn0031208'],
                               }

    # Same thing for GTF test file . . .
    GTF_parent_check_level_1 = {
                                'exon:chr2L:7529-8116:+':['FBtr0300689','FBtr0300690'],
                                'exon:chr2L:8193-9484:+':['FBtr0300689'],
                                'exon:chr2L:8193-8589:+':['FBtr0300690'],
                                'exon:chr2L:8668-9484:+':['FBtr0300690'],
                                'exon:chr2L:10000-11000:-':['transcript_Fk_gene_1'],
                                'exon:chr2L:11500-12500:-':['transcript_Fk_gene_2'],
                                'CDS:chr2L:7680-8116:+':['FBtr0300689','FBtr0300690'],
                                'CDS:chr2L:8193-8610:+':['FBtr0300689'],
                                'CDS:chr2L:8193-8589:+':['FBtr0300690'],
                                'CDS:chr2L:8668-9276:+':['FBtr0300690'],
                                'CDS:chr2L:10000-11000:-':['transcript_Fk_gene_1'],
                                'FBtr0300689':['FBgn0031208'],
                                'FBtr0300690':['FBgn0031208'],
                                'transcript_Fk_gene_1':['Fk_gene_1'],
                                'transcript_Fk_gene_2':['Fk_gene_2'],
                                'start_codon:chr2L:7680-7682:+':['FBtr0300689','FBtr0300690'],
                                'start_codon:chr2L:10000-11002:-':['transcript_Fk_gene_1'],
                                'stop_codon:chr2L:8611-8613:+':['FBtr0300689'],
                                'stop_codon:chr2L:9277-9279:+':['FBtr0300690'],
                                'stop_codon:chr2L:11001-11003:-':['transcript_Fk_gene_1'],
                                }


    GTF_parent_check_level_2 = {
            'exon:chr2L:7529-8116:+':['FBgn0031208'],
                                'exon:chr2L:8193-9484:+':['FBgn0031208'],
                                'exon:chr2L:8193-8589:+':['FBgn0031208'],
                                'exon:chr2L:8668-9484:+':['FBgn0031208'],
                                'exon:chr2L:10000-11000:-':['Fk_gene_1'],
                                'exon:chr2L:11500-12500:-':['Fk_gene_2'],
                                'CDS:chr2L:7680-8116:+':['FBgn0031208'],
                                'CDS:chr2L:8193-8610:+':['FBgn0031208'],
                                'CDS:chr2L:8193-8589:+':['FBgn0031208'],
                                'CDS:chr2L:8668-9276:+':['FBgn0031208'],
                                'CDS:chr2L:10000-11000:-':['Fk_gene_1'],
                                'FBtr0300689':['FBgn0031208'],
                                'FBtr0300690':['FBgn0031208'],
                                'transcript_Fk_gene_1':['Fk_gene_1'],
                                'transcript_Fk_gene_2':['Fk_gene_2'],
                                'start_codon:chr2L:7680-7682:+':['FBgn0031208'],
                                'start_codon:chr2L:10000-11002:-':['Fk_gene_1'],
                                'stop_codon:chr2L:8611-8613:+':['FBgn0031208'],
                                'stop_codon:chr2L:9277-9279:+':['FBgn0031208'],
                                'stop_codon:chr2L:11001-11003:-':['Fk_gene_1'],
                               }

    expected_feature_counts = {
                'GFF':{'gene':3,
                       'mRNA':4,
                       'exon':6,
                       'CDS':5,
                       'five_prime_UTR':1,
                       'intron':3,
                       'pcr_product':1,
                       'protein':2,
                       'three_prime_UTR':2},
                'GTF':{'gene':3,
                       'mRNA':4,
                       'CDS':5,
                       'exon':6,
                       'start_codon':2,
                       'stop_codon':3}
                }

    expected_features = {'GFF':['gene',
                                'mRNA',
                                'protein',
                                'five_prime_UTR',
                                'three_prime_UTR',
                                'pcr_product',
                                'CDS',
                                'exon',
                                'intron'],
                        'GTF':['gene',
                               'mRNA',
                               'CDS',
                               'exon',
                               'start_codon',
                               'stop_codon']}

    return GFF_parent_check_level_1,GFF_parent_check_level_2,GTF_parent_check_level_1,GTF_parent_check_level_2,expected_feature_counts,expected_features

(
GFF_parent_check_level_1,
GFF_parent_check_level_2,
GTF_parent_check_level_1,
GTF_parent_check_level_2,
expected_feature_counts,
expected_features,
) = EXPECTED_DATA()

def test_clean_gff():
    # test the "full" cleaning -- remove some featuretypes, do sanity-checking,
    # add chr
    fn = gffutils.example_filename('dirty.gff')
    gffutils.clean_gff(fn, newfn='cleaned.tmp',featuretypes_to_remove=['pcr_product','protein'],addchr=True)
    observed = open('cleaned.tmp').readlines()
    expected = open(gffutils.example_filename('fully-cleaned.gff')).readlines()
    assert observed==expected
    os.unlink('cleaned.tmp')
    gffutils.clean_gff(fn, featuretypes_to_remove=None, sanity_check=False)
    observed = open(gffutils.example_filename('dirty.gff.cleaned')).read()
    expected = open(gffutils.example_filename('basic-cleaned.gff')).read()
    assert observed == expected
    os.unlink(gffutils.example_filename('dirty.gff.cleaned'))


def test_sanitize_gff():
    """
    Test sanitization of GFF. Should be merged with GFF cleaning
    I believe unless they are intended to have different functionalities.
    """
    # Get unsanitized GFF
    fn = gffutils.example_filename("unsanitized.gff")
    # Get its database
    db_fname = helpers.get_db_fname(fn)
    # Sanitize the GFF
    sanitized_recs = helpers.sanitize_gff(db_fname)
    # Ensure that sanitization work, meaning all
    # starts must be less than or equal to stops
    for rec in sanitized_recs:
        assert (rec.start <= rec.stop), "Sanitization failed."
    # Remove temporary db file
    os.unlink(db_fname)
    print "Sanitized GFF successfully."


def test_inspect_featuretypes():
    observed = gffutils.inspect_featuretypes(gffutils.example_filename('FBgn0031208.gff'))
    observed.sort()
    expected = ['CDS', 'exon', 'five_prime_UTR', 'gene', 'intron', 'mRNA', 'pcr_product', 'protein', 'three_prime_UTR']
    print observed
    print expected
    assert observed == expected

class GenericDBClass(object):
    featureclass = None
    def setup(self):
        """
        Creates a new GFFDB or GTFDB (depending on self.__class__.featureclass)
        """
        self.featureclass = self.__class__.featureclass
        self.Feature = gffutils.Feature
        if self.featureclass == 'GFF':
            extension = '.gff'
            self.fn = gffutils.example_filename('FBgn0031208.gff')
            self.dbfn = testdbfn_gff
        if self.featureclass == 'GTF':
            extension = '.gtf'
            self.fn = gffutils.example_filename('FBgn0031208.gtf')
            self.dbfn = testdbfn_gtf

        self.G = gffutils.FeatureDB(self.dbfn)
        self.conn = sqlite3.connect(self.dbfn)
        self.c = self.conn.cursor()

    def table_test(self):
        #Right tables exist?
        expected_tables = ['features','relations','meta']
        expected_tables.sort()
        self.c.execute('select name from sqlite_master where type="table"')
        observed_tables = [str(i[0]) for i in self.c]
        observed_tables.sort()
        print expected_tables
        print observed_tables
        assert expected_tables == observed_tables

    def _count1(self,featuretype):
        # Count using SQL
        self.c.execute('select count() from features where featuretype = ?',(featuretype,))
        results = self.c.fetchone()[0]
        print 'count1("%s") says: %s' % (featuretype,results)
        return results

    def _count2(self,featuretype):
        # Count GFF lines.
        cnt = 0
        for line in open(self.fn):
            if line.startswith('#'):
                continue
            L = line.split()

            if len(L) < 3:
                continue

            if L[2] == featuretype:
                cnt += 1
        print 'count2("%s") says: %s' % (featuretype, cnt)
        return cnt

    def _count3(self,featuretype):
        # Count with the count_features_of_type method.
        results = self.G.count_features_of_type(featuretype)
        print 'count3("%s") says: %s' % (featuretype, results)
        return results

    def _count4(self,featuretype):
        # Count by iterating over all features of this type
        cnt = 0
        for i in self.G.features_of_type(featuretype):
            cnt += 1
        print 'count4("%s") says: %s' % (featuretype,cnt)
        return cnt

    def featurecount_test(self):
        #  Right number of each featuretype, using 3 different ways of
        #  counting?
        featuretypes = ['gene',
                        'mRNA',
                        'CDS',
                        'exon',
                        'five_prime_UTR',
                        'three_prime_UTR',
                        'pcr_product',
                        'protein','intron']
        for featuretype in featuretypes:
            rawsql_cnt = self._count1(featuretype)
            count_feature_of_type_cnt = self._count3(featuretype)
            iterator_cnt = self._count4(featuretype)
            try:
                hard_count = expected_feature_counts[self.featureclass][featuretype]
            except KeyError:
                hard_count = 0

            # count2 is not an appropriate test for GTF files, since "gene" is
            # not explicitly listed -- only implied by the boundaries of CDSs:
            #
            if self.featureclass == 'GFF':
                gffparsed_cnt = self._count2(featuretype)
                assert rawsql_cnt == count_feature_of_type_cnt == iterator_cnt == gffparsed_cnt == hard_count

            if self.featureclass == 'GTF':
                print 'hard count:',hard_count
                assert rawsql_cnt == count_feature_of_type_cnt == iterator_cnt == hard_count

    def total_features_test(self):
        # did all features in the GFF file make it into the database?

        # Doesn't make sense for GTF, which has gene features implied rather
        # than explicitly stated.
        if self.featureclass == 'GTF':
            return
        cnt = 0
        if self.__class__.featureclass == 'GFF':
            iterator = gffutils.GFFFile(self.fn)
        if self.__class__.featureclass == 'GTF':
            iterator = gffutils.GTFFile(self.fn)
        for feature in iterator:
            cnt += 1
        self.c.execute('select count() from features')
        total = self.c.fetchone()[0]
        assert cnt == total

    def parents_test(self):
        # DB retrieval of parents matches expected?
        #
        # Checks the hand-entered lookup dicts at the beginning of this module
        # to make sure parents match up.
        if self.featureclass == 'GFF':
            parents1 = GFF_parent_check_level_1
            parents2 = GFF_parent_check_level_2
        if self.featureclass == 'GTF':
            parents1 = GTF_parent_check_level_1
            parents2 = GTF_parent_check_level_2
        for child, expected_parents in parents1.items():
            observed_parents = [i.id for i in self.G.parents(child, level=1)]
            print 'observed parents for %s:' % child, set(observed_parents)
            print 'expected parents for %s:' % child, set(expected_parents)
            assert set(observed_parents) == set(expected_parents)

    def identity_test(self):
        # Actual string in file identical to tostring() method output?

        for i in open(self.fn):
            if i.startswith('#'):
                continue
            break
        first_line = i.rstrip()
        iterator = iter(gffutils.GFFFile(self.fn))

        first_feature = iterator.next()
        feature_string = first_feature.tostring()

        print 'first line:',first_line
        print 'first feat:',first_feature.tostring()
        assert feature_string == first_line

    def all_test(self):
        # all() returns expected number of features?
        results = list(self.G.all())
        if self.featureclass == 'GFF':
            print len(results)
            assert len(results) == 27
        if self.featureclass == 'GTF':
            print len(results)

            # 23 entries;
            #  3 genes, but 1 is noncoding
            #  4 transcripts (2 for one gene, one for the fake coding and one for the fake non-coding
            #  6 exons (2 in one isoform, 3 in the other (one of which is actually shared), 1 for each fake)
            #  5 CDS (cause one gene is non-coding)
            #  2 start_codons (1 shared between isoforms, one for fake coding)
            #  3 stop_codons (1 for each coding transcript)
            assert len(results) == 23

    def features_of_type_test(self):
        # features_of_type() returns expected number of features?
        d = expected_feature_counts[self.featureclass]
        for key,val in d.items():
            observed = len(list(self.G.features_of_type(key)))
            print 'key:',"'"+key+"'",'val:',val,'observed:', observed
            assert observed == val

        # now either catch all...
        for key,val in d.items():
            observed = len(list(self.G.features_of_type(key, chrom='chr2L', start=1, stop=100000)))
            assert observed == val

        # or none...
        for key,val in d.items():

            # wrong chrom should return 0
            observed = len(list(self.G.features_of_type(key, chrom='chrX', strand='+', start=1, stop=10000)))
            assert observed == 0

            # wrong strand should return 0
            observed = list(self.G.features_of_type(key, chrom='chr2L', strand='-', start=9999, stop=100000))
            expected_len = 2
            if key == 'gene' or key == 'mRNA':
                print 'observed:',observed
                print 'expected len:',expected_len
                assert len(observed) == expected_len


            # too far into chrom should return 0
            observed = len(list(self.G.features_of_type(key, chrom='chr2L', strand='+', start=100000, stop=1e6)))
            assert observed == 0

            # reversed start/stop should return 0
            observed = len(list(self.G.features_of_type(key, chrom='chr2L', start=10000, stop=1)))
            assert observed == 0

    def features_test(self):
        # All featuretypes present and accounted for?
        expected = expected_features[self.featureclass]
        results = list(self.G.featuretypes())
        assert set(results) == set(expected)

    def strand_test(self):
        # Expected strands in db?
        assert set(self.G.strands()) == set(['-','+'])

    def chrom_test(self):
        # Expected chromosomes in db?
        # Get the chromosomes that are in the GFF/GTF file, and make sure
        # they made it into the database.
        gffchroms = []
        for line in open(self.fn):
            if line.startswith('>'):
                break
            if line.startswith('#'):
                continue
            L = line.split()
            if len(L) < 1:
                continue
            gffchroms.append(L[0])
        print 'observed:',set(self.G.chromosomes())
        print 'expected:',set(gffchroms)
        assert set(gffchroms) == set(self.G.chromosomes())

    def closest_features_test(self):
        # Expected closest features returned?

        # closest one to the beginning, on plus strand
        observed_dist, observed_feature = self.G.closest_feature(chrom='chr2L',
                                                                 pos=1,
                                                                 featuretype='gene',
                                                                 strand='+')
        print observed_feature
        assert observed_feature.id == 'FBgn0031208'

        # closest one to beginning, ignoring the first one.  Should return None.
        result = self.G.closest_feature(chrom='chr2L',
                                        pos=1,
                                        featuretype='gene',
                                        strand='+',
                                        ignore=['FBgn0031208'])
        print result
        assert result == (None,None)

        # should work the same with a string rather than list
        result = self.G.closest_feature(chrom='chr2L',
                                        pos=1,
                                        featuretype='gene',
                                        strand='+',
                                        ignore='FBgn0031208')
        print result
        assert result == (None,None)

        # closest mRNA to beginning, on - strand.
        observed_dist, observed_feature = self.G.closest_feature(chrom='chr2L',
                                                                 pos=1,
                                                                 featuretype='mRNA',
                                                                 strand='-',
                                                                 ignore=None,)
        print observed_feature
        assert observed_feature.id == 'transcript_Fk_gene_1'

        # TODO: the GFF/GTF files probably need some more genes added to be
        # able to test the "upstream" # and "downstream" functionality.

    def feature_not_found_test(self):
        # Correct exception thrown upon asking for nonexistent feature?
        try:
            self.G['i am not a real feature']
        except gffutils.FeatureNotFoundError:
            pass

        try:
            self.G['another fake one']
        except gffutils.FeatureNotFoundError as e:
            print e
            assert str(e) == 'another fake one'

    def getitem_and_eq_test(self):
        # test access of a string or a feature, make sure you get back the same
        # thing.

        if self.featureclass == 'GFF':
            expected = 'chr2L\tFlyBase\tgene\t7529\t9484\t.\t+\t.\tID=FBgn0031208;Name=CG11023;Ontology_term=SO:0000010,SO:0000087,GO:0008234,GO:0006508;Dbxref=FlyBase:FBan0011023,FlyBase_Annotation_IDs:CG11023,GB:AE003590,GB_protein:AAO41164,GB:AI944728,GB:AJ564667,GB_protein:CAD92822,GB:BF495604,UniProt/TrEMBL:Q6KEV3,UniProt/TrEMBL:Q86BM6,INTERPRO:IPR003653,BIOGRID:59420,dedb:5870,GenomeRNAi_gene:33155,ihop:59383;derived_computed_cyto=21A5-21A5;gbunit=AE014134'
        if self.featureclass == 'GTF':
            expected = 'chr2L	derived	gene	7529	9484	.	+	.	gene_id "FBgn0031208";'
            old_expected = """chr2L	protein_coding	exon	7529	8116	.	+	.	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	exon	7529	8116	.	+	.	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	start_codon	7680	7682	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	start_codon	7680	7682	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	CDS	7680	8116	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	CDS	7680	8116	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	CDS	8193	8589	.	+	2	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	exon	8193	8589	.	+	2	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	CDS	8193	8610	.	+	2	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	exon	8193	9484	.	+	.	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	stop_codon	8611	8613	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300689";
chr2L	protein_coding	CDS	8668	9276	.	+	2	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	exon	8668	9484	.	+	.	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
chr2L	protein_coding	stop_codon	9277	9279	.	+	0	gene_id "FBgn0031208"; transcript_id "FBtr0300690";
"""
        observed_feature_1 = self.G['FBgn0031208']

        observed_string_1 = observed_feature_1.tostring()

        #print 'expected :',expected
        #print 'observed1:',observed_string_1

        #d = difflib.ndiff(expected.splitlines(True), observed_string_1.splitlines(True))
        #print ''.join(d)
        print observed_string_1
        assert observed_string_1 == expected

        observed_feature_2 = self.G[observed_feature_1]

        observed_string_2 = observed_feature_2.tostring()
        print 'expected :',expected
        print 'observed2:',observed_string_2
        assert observed_string_2 == expected

        assert str(observed_feature_1) == str(observed_feature_2)

    def overlapping_features_test(self):
        # test everything against a hard-coded list.
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L', start=7529, stop=9484,completely_within=False)])
        print observed
        if self.featureclass == 'GFF':
            expected_hardcoded = [
                             'CG11023:1',
                             'CDS_FBgn0031208:1_737',
                             'CDS_FBgn0031208:2_737',
                             'CDS_FBgn0031208:3_737',
                             'CDS_FBgn0031208:4_737',
                             'FBgn0031208',
                             'exon:chr2L:8193-8589:+',
                             'FBgn0031208:3',
                             'FBgn0031208:4',
                             'FBpp0289913',
                             'FBpp0289914',
                             'FBtr0300689',
                             'FBtr0300690',
                             'INC121G01_pcr_product',
                             'five_prime_UTR_FBgn0031208:1_737',
                             'intron_FBgn0031208:1_FBgn0031208:2',
                             'intron_FBgn0031208:1_FBgn0031208:3',
                             'intron_FBgn0031208:2_FBgn0031208:4',
                             'three_prime_UTR_FBgn0031208:3_737',
                             'three_prime_UTR_FBgn0031208:4_737',
                             ]
        if self.featureclass == 'GTF':
            expected_hardcoded = [
                    'CDS:chr2L:7680-8116:+',
                    'CDS:chr2L:8193-8610:+',
                    'CDS:chr2L:8193-8589:+',
                    'CDS:chr2L:8668-9276:+',
                    'FBgn0031208',
                    'FBtr0300689',
                    'FBtr0300690',
                    'exon:chr2L:7529-8116:+',
                    'exon:chr2L:8193-9484:+',
                    'exon:chr2L:8193-8589:+',
                    'exon:chr2L:8668-9484:+',
                    'start_codon:chr2L:7680-7682:+',
                    'stop_codon:chr2L:8611-8613:+',
                    'stop_codon:chr2L:9277-9279:+']

        print 'observed:',set(observed)
        print 'expected:',set(expected_hardcoded)
        assert set(observed) == set(expected_hardcoded)

        # assert that features that overlap the gene contain the gene's children and grandchildren
        observed = [i.id for i in self.G.overlapping_features(chrom='chr2L', start=7529, stop=9484, featuretype='gene')]
        observed += [i.id for i in self.G.overlapping_features(chrom='chr2L', start=7529, stop=9484, featuretype='exon')]
        observed += [i.id for i in self.G.overlapping_features(chrom='chr2L', start=7529, stop=9484, featuretype='intron')]
        observed += [i.id for i in self.G.overlapping_features(chrom='chr2L', start=7529, stop=9484, featuretype='mRNA')]
        observed.sort()

        expected_generated = list(self.G.children('FBgn0031208',level=1,featuretype='mRNA'))
        expected_generated += list(self.G.children('FBgn0031208',level=2,featuretype='exon'))
        expected_generated += list(self.G.children('FBgn0031208',level=2,featuretype='intron'))
        expected_generated.append(self.G['FBgn0031208'])
        expected_generated = sorted([i.id for i in expected_generated])
        print observed
        print expected_generated
        print set(observed).difference(expected_generated)
        assert observed == expected_generated

        # check that the first exon, which is chr2L:7529-8116, overlaps lots of stuff....
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L',start=7529,stop=8116, completely_within=False, strand='+')])
        print 'observed:',observed
        if self.featureclass == 'GFF':
            expected = ['CDS_FBgn0031208:1_737',
                        'CG11023:1',
                        'FBgn0031208',
                        'FBpp0289913',
                        'FBpp0289914',
                        'FBtr0300689',
                        'FBtr0300690',
                        'five_prime_UTR_FBgn0031208:1_737',
                        ]
        if self.featureclass == 'GTF':
            # things like the last exons and stop codons shouldn't be overlapping.
            expected = ['CDS:chr2L:7680-8116:+',
                        'FBgn0031208',
                        'FBtr0300689',
                        'FBtr0300690',
                        'exon:chr2L:7529-8116:+',
                        'start_codon:chr2L:7680-7682:+']
        print 'expected:',expected
        assert observed == expected

        # on the opposite strand, though, you should have nothing.
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L',start=7529,stop=8116, completely_within=False, strand='-')])
        assert observed == []


        # completely_within, however, should only return the UTR, exon, and CDS for GFF, (and exon, CDS, and start codon for GTF)
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L',start=7529,stop=8116, completely_within=True)])
        print 'observed:',observed
        if self.featureclass == 'GFF':
            expected = [
                        'CDS_FBgn0031208:1_737',
                        'CG11023:1',
                        'five_prime_UTR_FBgn0031208:1_737',]
        if self.featureclass == 'GTF':
            # multiple exons, multiple CDSs, multiple start_codons.  Still not
            # sure if this is the best way to do it, since it's not identical
            # to GFF output.
            expected = [
                    'CDS:chr2L:7680-8116:+',
                    'exon:chr2L:7529-8116:+',
                    'start_codon:chr2L:7680-7682:+']
        print 'expected:',expected
        assert observed == expected

        # stop truncated by 1 bp should only get you the UTR for GFF, or just the start codon[s] for GTF.
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L',start=7529,stop=8115, completely_within=True)])
        print 'observed:',observed
        if self.featureclass == 'GFF':
            expected = ['five_prime_UTR_FBgn0031208:1_737']
        if self.featureclass == 'GTF':
            expected = ['start_codon:chr2L:7680-7682:+']
        print 'expected:',expected
        assert observed == expected

        # and the 5'UTR, but with start truncated 1 bp, should get you nothing -- for both GFF and GTF.
        observed = sorted([i.id for i in self.G.overlapping_features(chrom='chr2L',start=7530,stop=7679, completely_within=True)])
        print 'observed:',observed
        expected = []
        print 'expected:',expected
        assert observed == expected

    def merge_features_test(self):
        defaults = dict(chrom='.', source='.', featuretype='.', start=1, stop=2, score='.', frame='.', attributes='')

        features_to_merge = []
        chrom = 'chr2L'
        coords = [(1,10,'exon'), (5,50,'intron'), (100,105,'CDS')]
        for start, stop, featuretype in coords:
            feature = self.Feature(
                    chrom=chrom,
                    source='.', 
                    featuretype=featuretype,
                    start=start,
                    stop=stop,
                    score='.', 
                    strand='.', 
                    frame='.',
                    attributes='')
            features_to_merge.append(feature)
        observed = list(self.G.merge_features(features_to_merge))
        expected = [
                self.Feature(
                    chrom=chrom,
                    source='.', 
                    featuretype='merged_CDS_exon_intron',
                    start=1,
                    stop=50,
                    score='.', 
                    strand='.', 
                    frame='.',
                    attributes=''),
                self.Feature(
                    chrom=chrom,
                    source='.', 
                    featuretype='merged_CDS_exon_intron',
                    start=100,
                    stop=105,
                    score='.', 
                    strand='.', 
                    frame='.',
                    attributes='')]

        print 'observed:', observed
        print 'expected:',expected
        assert observed == expected

        # make sure you complain if more than one strand and ignore_strand=False
        diff_strands = [
                self.Feature(
                    chrom=chrom,
                    source='.', 
                    featuretype='.',
                    start=1,
                    stop=10,
                    score='.', 
                    strand='+', 
                    frame='.',
                    attributes=''),
                self.Feature(
                    chrom=chrom,
                    source='.', 
                    featuretype='.',
                    start=5,
                    stop=20,
                    score='.', 
                    strand='-', 
                    frame='.',
                    attributes=''),
           ] 
        merged = self.G.merge_features(diff_strands)
        nt.assert_raises(ValueError, list, merged)

        # But this should run without raising an error
        merged = list(self.G.merge_features(diff_strands,ignore_strand=True))

        diff_chroms = [

                self.Feature(
                    chrom='chr2L',
                    source='.', 
                    featuretype='.',
                    start=1,
                    stop=10,
                    score='.', 
                    strand='+', 
                    frame='.',
                    attributes=''),
                self.Feature(
                    chrom='chrX',
                    source='.', 
                    featuretype='.',
                    start=5,
                    stop=20,
                    score='.', 
                    strand='+', 
                    frame='.',
                    attributes=''),
           ] 
        merged = self.G.merge_features(diff_chroms)
        nt.assert_raises(NotImplementedError, list, merged)
        exons = self.G.children('FBgn0031208',featuretype='exon', level=2)
        merged_exons = self.G.merge_features(exons)
        observed = list(merged_exons)

        expected = [
                    self.Feature(chrom='chr2L',start=7529,stop=8116, strand='+', featuretype='merged_exon'),
                    self.Feature(chrom='chr2L',start=8193,stop=9484, strand='+', featuretype='merged_exon'),
                   ]

        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected

    def interfeatures_test(self):
        chrom = 'chr2L'
        coords = [(1,10,'exon'), (50,100,'exon'), (200,300,'other')]
        features = []
        for start,stop,featuretype in coords:
            features.append(self.Feature(
                chrom=chrom,
                source='.',
                featuretype=featuretype,
                start=start,
                stop=stop,
                score='.',
                strand='.',
                frame='.',
                attributes=''))
        observed = list(self.G.interfeatures(features))

        expected = [
                self.Feature(
                    chrom=chrom,
                    source='.',
                    featuretype='inter_exon_exon',
                    start=11,
                    stop=49,
                    score='.',
                    strand='.',
                    frame='.',
                    attributes=''),

                self.Feature(
                    chrom=chrom,
                    source='.',
                    featuretype='inter_exon_other',
                    start=101,
                    stop=199,
                    score='.',
                    strand='.',
                    frame='.',
                    attributes='')]
        print 'observed:', observed
        print 'expected:', expected
        assert observed == expected

    def execute_test(self):
        query = 'SELECT id, chrom, start, stop FROM features WHERE id = "FBgn0031208"'
        expected = [('FBgn0031208','chr2L',7529,9484)]
        observed = list(self.G.execute(query))
        print observed
        print expected
        assert observed == expected


    def reflat_test(self):
        gene_id = 'FBgn0031208'
        gene = self.G[gene_id]
        observed = ''.join(self.G.refFlat(gene))
        expected = """FBtr0300689	FBgn0031208	chr2L	+	7529	9484	7680	8610	2	7529,8193,	8116,9484,
FBtr0300690	FBgn0031208	chr2L	+	7529	9484	7680	9276	3	7529,8193,8668,	8116,8589,9484,
"""
        print 'observed:'
        print observed
        print 'expected:'
        print expected
        assert observed == expected

    def test_n_isoforms(self):
        assert self.G.n_gene_isoforms('FBgn0031208') == self.G.n_gene_isoforms(self.G['FBgn0031208']) == 2

    def promoter_test(self):
        # test defaults of bidirectional=True and dist=1000
        print 'original:', self.G['FBgn0031208']
        observed = self.G.promoter(id='FBgn0031208', direction='both')
        expected = self.Feature(chrom='chr2L', source='imputed', start=6529,stop=8529,strand='+')
        expected.featuretype = 'promoter'
        print 'observed:'
        print observed
        print 'len(observed):',len(observed)
        print 'expected:'
        print expected

        # 1000 upstream and the TSS itself.
        assert len(observed) == 2001
        assert observed == expected


        # same if Feature rather than string is provided
        observed = self.G.promoter(id=self.G['FBgn0031208'], direction='both')
        expected = self.Feature(chrom='chr2L', source='imputed', start=6529,stop=8529,strand='+')
        expected.featuretype = 'promoter'
        print 'observed:'
        print observed
        print 'len(observed):',len(observed)
        print 'expected:'
        print expected

        # 1000 upstream and the TSS itself.
        assert len(observed) == 2001
        assert observed == expected


        # Test various kwargs
        observed = self.G.promoter(id='FBgn0031208',dist=100)
        expected = self.Feature(chrom='chr2L',start=7429,stop=7529,strand='+', featuretype='promoter', source='imputed')
        print 'observed:'
        print observed
        print 'len(observed):',len(observed)
        print 'expected:'
        print expected
        assert len(observed) == 101
        assert observed == expected


        # Test various kwargs
        observed = self.G.promoter(id='FBgn0031208',dist=100,direction='downstream')
        expected = self.Feature(chrom='chr2L',start=7529,stop=7629,strand='+')
        expected.featuretype = 'promoter'
        expected.source = 'imputed'
        print 'observed:'
        print observed
        print 'len(observed):',len(observed)
        print 'expected:'
        print expected
        assert len(observed) == 101
        assert observed == expected


        # Test truncation
        # TODO: add another gene in GTF file....
        if self.featureclass == 'GFF':
            observed = self.G.promoter(id='Fk_gene_1',dist=5000,truncate_at_next_feature='gene')
            expected = self.Feature(chrom='chr2L',start=11000,stop=11500,strand='-')
            expected.featuretype = 'promoter'
            expected.source = 'imputed'
            print 'observed:'
            print observed
            print 'len(observed):',len(observed)
            print 'expected:'
            print expected
            assert len(observed) == 501
            assert observed == expected

    def attribute_search_test(self):
        if self.featureclass == 'GFF':
            observed = list(self.G.attribute_search('FBan0011023'))
            expected = self.G['FBgn0031208']
            assert len(observed)==1
            assert str(observed[0]) == str(expected)

        if self.featureclass == 'GTF':
            observed = list(self.G.attribute_search('Fk_gene_1'))
            expected = self.G['Fk_gene_1']
            assert len(observed)==1
            assert str(observed[0]) == str(expected)

    def exonic_bp_test(self):
        expected = 1880
        observed1 = self.G.exonic_bp('FBgn0031208')

        # should work the same if you provide a Feature
        observed2 = self.G.exonic_bp(self.G['FBgn0031208'])
        assert observed1 == observed2 == expected


        # If no exons, then exonic length is zero
        observed = self.G.exonic_bp('transcript_Fk_gene_1')
        expected = 0
        assert observed == expected

    def random_feature_test(self):
        # really all we can do is make sure the featuretype is correct and that
        # upon retrieving the same feature from the DB, we get identity.
        random_gene = self.G.random_feature('gene')
        assert random_gene.featuretype == 'gene'
        assert self.G[random_gene.id] == random_gene

    def coding_genes_test(self):
        observed = sorted([i.id for i in self.G.coding_genes()])
        expected = ['FBgn0031208','Fk_gene_1']
        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected

    def n_exon_isoforms_test(self):
        exons = list(self.G.children('FBgn0031208',level=2, featuretype='exon'))
        exons.sort(key=lambda x: x.start)
        exon = exons[0]
        observed = self.G.n_exon_isoforms(exon)
        expected = 2
        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected

    def exons_gene_test(self):
        # exons_gene uses a different query than the [already-tested] children.
        # So hopefully this isn't a tautology
        exons = list(self.G.children('FBgn0031208',level=2, featuretype='exon'))
        exons.sort(key=lambda x: x.start)
        exon = exons[0]
        observed = self.G.exons_gene(exon)
        expected = 'FBgn0031208'
        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected

    def teardown(self):
        pass
        #os.unlink(testdbfn)

    def test_too_deep(self):
        def f():
            list(self.G.children('FBgn0031208', level=3))
        nt.assert_raises(NotImplementedError, f)

        def f():
            list(self.G.parents('FBgn0031208', level=3))
        nt.assert_raises(NotImplementedError, f)


class TestGFFDBClass(GenericDBClass):
    featureclass = 'GFF'

class TestGTFDBClass(GenericDBClass):
    featureclass = 'GTF'
    def UTR_(self):

        observed = self.G.UTRs(self.G['FBtr0300689'])
        expected = [
                    self.Feature(chrom='chr2L',start=7529,stop=7679,strand='+',featuretype='five_prime_UTR'),
                    self.Feature(chrom='chr2L',start=8611,stop=9484,strand='+',featuretype='three_prime_UTR'),
                   ]
        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected

        observed = self.G.UTRs(self.G['FBtr0300690'])
        expected = [
                    self.Feature(chrom='chr2L',start=7529,stop=7679,strand='+',featuretype='five_prime_UTR'),
                    self.Feature(chrom='chr2L',start=9277,stop=9484,strand='+',featuretype='three_prime_UTR'),
                   ]
        print 'observed:',observed
        print 'expected:',expected
        assert observed == expected


def test_empty_superclass_methods():
    dbcreator = gffutils.db.DBCreator(gffutils.example_filename('FBgn0031208.gff'), 'empty.db', verbose=False)
    dbcreator.populate_from_features([])
    dbcreator.update_relations()
    assert os.path.exists('empty.db')
    assert os.stat('empty.db').st_size == 0
    os.unlink('empty.db')

def test_force_removes_file():
    os.system('echo "something" > empty.db')
    dbcreator = gffutils.db.DBCreator(gffutils.example_filename('FBgn0031208.gff'), 'empty.db', verbose=False, force=True)
    assert os.path.exists('empty.db')
    assert os.stat('empty.db').st_size == 0
    os.unlink('empty.db')

def test_verbose():
    # just a smoke test to make sure it runs
    actual_stderr = sys.stderr
    import StringIO
    sys.stderr = StringIO.StringIO()
    gffdb = gffutils.db.GFFDBCreator(gffutils.example_filename('FBgn0031208.gff'),
            'deleteme.db', verbose=True, force=True).create()
    sys.stderr = actual_stderr
    os.unlink('deleteme.db')

def __test_attributes_modify():
    """
    Test that attributes can be modified in a GFF record.

    TODO: This test case fails?
    """
    # Test that attributes can be modified
    gffutils.create_db(gffutils.example_filename('FBgn0031208.gff'), testdbfn_gff,
                       verbose=False,
                       force=True)
    db = gffutils.FeatureDB(testdbfn_gff)
    gene_id = "FBgn0031208"
    gene_childs = list(db.children(gene_id))
    print "First child is not an mRNA"
    print gene_childs[0].featuretype
    assert str(gene_childs[0].attributes) == 'ID=FBtr0300689;Name=CG11023-RB;Parent=FBgn0031208;Dbxref=FlyBase_Annotation_IDs:CG11023-RB;score_text=Strongly Supported;score=11'
    gene_childs[0].attributes["ID"] = "Modified"
    assert str(gene_childs[0].attributes) == 'ID=Modified;Name=CG11023-RB;Parent=FBgn0031208;Dbxref=FlyBase_Annotation_IDs:CG11023-RB;score_text=Strongly Supported;score=11;ID=Modified'
    ###
    ### NOTE: Would be ideal if database checked that this
    ### change leaves "dangling" children; i.e. children
    ### GFF nodes that point to Parent that does not exist.
    ###
    

if __name__ == "__main__":
    # this test case fails
    #test_attributes_modify()
    test_sanitize_gff()
