#!/usr/bin/env python

import sys
#If the module dbpediaEnquirerPy is no the python path (or same folder) you don't need to see this, this is just for this example script.
sys.path.append('../')


from dbpediaEnquirerPy import *



if __name__ == '__main__':
    my_dbpedia = Cdbpedia_enquirer()
    dblink = 'http://dbpedia.org/resource/Tom_Cruise'
    dblink = 'http://dbpedia.org/resource/El_Tiempo_(Honduras)'
    print 'WIKIPAGEID:',my_dbpedia.get_wiki_page_id_for_dblink(dblink)
    print 'Dblink:',dblink
    print '\tWordnet type:',     my_dbpedia.get_wordnet_type_for_dblink(dblink)
    print '\tWikipedia page id:',my_dbpedia.get_wiki_page_id_for_dblink(dblink)
    print '\tOntology labels:',  my_dbpedia.get_dbpedia_ontology_labels_for_dblink(dblink)
    print
    ###############
    # Ontology examples
    ##############
    
    
    ontology = Cdbpedia_ontology()
    
    onto_label = 'http://dbpedia.org/ontology/RallyDriver'
    print 'Ontological path for', onto_label, ontology.get_ontology_path(onto_label)
    print 'Depth in ontology:',ontology.get_depth(onto_label)
