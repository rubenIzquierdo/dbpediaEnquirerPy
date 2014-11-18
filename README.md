#dbpediaEnquirerPy#


This library provides classes and functions to query DBpedia using SPARQL and the DBpedia ontology. For querying DBpedia we make use of the
[Virtuoso SPARQL endpoint](http://dbpedia.org/sparql) and the python library [SPARQLWrapper](http://rdflib.github.io/sparqlwrapper/) that enables the usage of SPARQL and RDF from python.
Regarding the ontology, the OWL file from DBpedia defining the ontology is automatically downloaded and exploited locally with python functions.

##Usage##

This repository is a python module itself, so, once installed it can be imported from your own python script and use the classes available to query dbpedia and the ontology. This would be a simple
example (this example can be found in the file `example.py`):

```python
import sys
from dbpediaEnquirerPy import *

if __name__ == '__main__':
    my_dbpedia = Cdbpedia_enquirer()
    dblink = 'http://dbpedia.org/resource/Tom_Cruise'
    print 'Dblink:',dblink
    print '\tWordnet type:',     my_dbpedia.get_wordnet_type_for_dblink(dblink)
    print '\tWikipedia page id:',my_dbpedia.get_wiki_page_id_for_dblink(dblink)
    print '\tOntology labels:',  my_dbpedia.get_dbpedia_ontology_labels_for_dblink(dblink)
    
    ## Ontology example
    ontology = Cdbpedia_ontology()
    
    onto_label = 'http://dbpedia.org/ontology/RallyDriver'
    print 'Ontological path for',onto_label,'=>',ontology.get_ontology_path(onto_label)    
    print 'Depth in ontology:',ontology.get_depth(onto_label)
```

If you run this (after the installation) the output should be similar to:
```shell
Dblink: http://dbpedia.org/resource/Tom_Cruise
	Wordnet type: synset-actor-noun-1
	Wikipedia page id: 31460
	Ontology labels: ['http://dbpedia.org/ontology/Agent', 'http://dbpedia.org/ontology/Person']

Ontological path for http://dbpedia.org/ontology/RallyDriver ['http://dbpedia.org/ontology/RallyDriver', 'http://dbpedia.org/ontology/RacingDriver', 'http://dbpedia.org/ontology/MotorsportRacer', 'http://dbpedia.org/ontology/Athlete', 'http://dbpedia.org/ontology/Person', 'http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing']
Depth in ontology: 7
```

## Quick Installation##

An automatic installation script is provided with this repository. It will install and download automatically all the requirements (the are basically two requirements for this repository, the SPARQLWrapper library and the DBpedia ontology in OWL). So the basic
steps to get this repository working from the scratch would be:
```shell
cd your_local_folder
git clone https://github.com/rubenIzquierdo/dbpediaEnquirerPy
cd dbpediaEnquirerPy
. install_dependencies.sh
```

These lines should install all the required dependencies. You can test if the installation is valid by running the example `python example.py`.
##Documentation##

All the classes and methods are extensively described in an API that can be found in different formats:

1. HTML: [http://kyoto.let.vu.nl/~izquierdo/api/dbpediaEnquirerPy/](http://kyoto.let.vu.nl/~izquierdo/api/dbpediaEnquirerPy/)
2. PDF: [http://kyoto.let.vu.nl/~izquierdo/api/dbpediaEnquirerPy/api.pdf](http://kyoto.let.vu.nl/~izquierdo/api/dbpediaEnquirerPy/api.pdf)

You can also build the documentation locally by running the script `. build_documentation.sh`, which would generate a folder `apidocs` with the whole documentation (you will need
epydoc installed in order to generate the documentation)

##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
* http://rubenizquierdobevia.com/

##License##

Sofware distributed under GPL.v2, see LICENSE file for details.


