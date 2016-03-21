#!/usr/bin/env python

from __future__ import print_function


"""
This module contains two classes that encapsulate and provide access to DBpedia online (using SPARQL and a cache method for efficiency)
and another one to access and query the DBpedia ontology. There are two main classes to provide this functionality:

  1. B{Cdbpedia_ontology}: provides access to the DBpedia ontology
  2. B{Cdbpedia_enquirer}: allows to query DBpedia using Virtuoso SPARQL endpoint

@author: U{Ruben Izquierdo Bevia<rubenizquierdobevia.com>}
@version: 0.1
@contact: U{ruben.izquierdobevia@vu.nl<mailto:ruben.izquierdobevia@vu.nl>} 
@contact: U{rubensanvi@gmail.com<mailto:rubensanvi@gmail.com>}
@contact: U{rubenizquierdobevia.com}
@since: 17-Nov-2014
"""

__version__ = '0.1'
__modified__ = '17Nov2014'
__author__ = 'Ruben Izquierdo Bevia'

##### Changes ##############
# v0.1 ==> basic functions and methods
#
################################


import json
import sys
import os
import hashlib
import pickle
import urllib
#import urllib.request, urllib.parse, urllib.error

from SPARQLWrapper import SPARQLWrapper, JSON
from .resources import OWL_FILE


class Cdbpedia_ontology:
    '''
    This class encapsulates the dbpedia ontology and gives acces to it
    '''
    def __init__(self):
        self.__resource_folder__ = os.path.dirname(os.path.realpath(__file__))+'/resources'
        self.list_labels = set()                             #An unique list of ontology labels
        self.superclass_for_class = {}
        self.__load_subclasses__()
        self.__nsmap = {}   ##mapping of namespaces
        
        
    
    def __get_owl_root_node__(self):
        try:
            from lxml import etree
        except:
            import xml.etree.cElementTree as etree
        owl_file = self.__resource_folder__+'/'+OWL_FILE
        owl_root = etree.parse(owl_file).getroot()
        self.nsmap = owl_root.nsmap.copy()
        self.nsmap['xmlns'] = self.nsmap.pop(None)
        return owl_root
    
    
    def __load_subclasses__(self):
        owl_root = self.__get_owl_root_node__()
        for class_obj in owl_root.findall('{%s}Class' % owl_root.nsmap['owl']):
            onto_label = class_obj.get('{%s}about' % owl_root.nsmap['rdf'])
            self.list_labels.add(onto_label)
            subclass_of_obj = class_obj.find('{%s}subClassOf' % owl_root.nsmap['rdfs'])
            if subclass_of_obj is not None:
                superclass_label = subclass_of_obj.get('{%s}resource' % owl_root.nsmap['rdf'])
                self.superclass_for_class[onto_label] = superclass_label

    def is_leaf_class(self,onto_label):
        """
        Checks if the ontology label provided (for instance http://dbpedia.org/ontology/SportsTeam) is a leaf in the DBpedia ontology tree or not 
        It is a leaf if it is not super-class of any other class in the ontology
        @param onto_label: the ontology label
        @type onto_label: string
        @return: whether it is a leaf or not
        @rtype: bool
        """
        is_super_class = False
        for subclass, superclass in list(self.superclass_for_class.items()):
            if superclass == onto_label:
                is_super_class = True
                break
        if not is_super_class and onto_label not in self.list_labels:
            return None
            
        return not is_super_class
    
    def get_ontology_path(self,onto_label):
        '''
        Returns the path of ontology classes for the given ontology label (is-a relations)
        @param onto_label: the ontology label (could be http://dbpedia.org/ontology/SportsTeam or just SportsTeam)
        @type onto_label: str
        @return: list of ontology labels
        @rtype: list
        '''
        thing_label = '%sThing' % self.nsmap['owl']
        if onto_label == thing_label:
            return [thing_label]
        else:
            if self.nsmap['xmlns'] not in onto_label:   #To allow things like "SportsTeam instead of http://dbpedia.org/ontology/SportsTeam
                onto_label = self.nsmap['xmlns']+onto_label
                
            if onto_label not in self.superclass_for_class:
                return []
            else:
                super_path = self.get_ontology_path(self.superclass_for_class[onto_label])
                super_path.insert(0,onto_label)
                return super_path
            
    def get_depth(self,onto_label):
        '''
        Returns the depth in the ontology hierarchy for the given ontology label (is-a relations)
        @param onto_label: the ontology label (could be http://dbpedia.org/ontology/SportsTeam or just SportsTeam)
        @type onto_label: str
        @return: depth
        @rtype: int
        '''
        path = self.get_ontology_path(onto_label)
        return len(path)
        
        


                
class Cdbpedia_enquirer:
    """
    This class allows to query dbpedia using the Virtuoso SPARQL endpoint and gives access to different type of information
    """
    def __init__(self, endpoint='http://dbpedia.org/sparql'):
        self.__endpoint__ = endpoint
        self.__thisfolder__ = os.path.dirname(os.path.realpath(__file__))
        self.__cache_folder__ = self.__thisfolder__+'/.dbpedia_cache'
        self.__dbpedia_ontology__ = Cdbpedia_ontology()
    
    def __get_name_cached_file(self,query):
        if isinstance(query,str):
            query = query.encode('utf-8')
        cached_file =self.__cache_folder__+'/'+hashlib.sha256(query).hexdigest()
        return cached_file
    
    def __get_name_cached_ontology_type(self,dblink):
        if isinstance(dblink,str):
            dblink = dblink.encode('utf-8')
        cached_file =self.__cache_folder__+'/'+hashlib.sha256(dblink).hexdigest()+'.ontologytype'
        return cached_file
        
    def __my_query(self,this_query):
        cached_file = self.__get_name_cached_file(this_query)
        if os.path.exists(cached_file):
            fd = open(cached_file,'rb')
            results = pickle.load(fd)
            fd.close()
        else:
            sparql = SPARQLWrapper(self.__endpoint__)
            sparql.setQuery(this_query)
            sparql.setReturnFormat(JSON)
            query   = sparql.query()
            #query.setJSONModule(json)
            results = query.convert()['results']['bindings']
            if not os.path.exists(self.__cache_folder__): 
                os.mkdir(self.__cache_folder__)
            fd = open(cached_file,'wb')
            pickle.dump(results, fd, protocol=-1)
            fd.close()
        return results
    
    def get_deepest_ontology_class_for_dblink(self,dblink):
        """
        Given a dblink (http://dbpedia.org/resource/Tom_Cruise) gets all the possible ontology classes from dbpedia,
        calculates the depth of each on in the DBpedia ontology and returns the deepest one
        @param dblink: the dbpedia link
        @type dblink: string
        @return: the deespest DBpedia ontology label
        @rtype: string
        """
        deepest = None
        onto_labels =  self.get_dbpedia_ontology_labels_for_dblink(dblink)
        pair_label_path = []
        for ontolabel in onto_labels:
            this_path = self.__dbpedia_ontology__.get_ontology_path(ontolabel)
            pair_label_path.append((ontolabel,len(this_path)))
        if len(pair_label_path) > 0:
            deepest = sorted(pair_label_path,key=lambda t: -t[1])[0][0]
        return deepest
    
    def get_all_instances_for_ontology_label(self,ontology_label,log=False):
        """
        Given an ontoloy label (like http://dbpedia.org/ontology/SportsTeam), it will return
        all the entities in DBPEDIA tagged with that label
        @param ontology_label: the ontology label (http://dbpedia.org/ontology/SportsTeam)
        @type ontology_label: str
        @param log: to get log information
        @type log: bool
        @return: list of all dbpedia entities belonging to that ontological type
        @rtype: list
        """

        instances = []
        keep_searching = True
        while keep_searching:
            query = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT ?entity
                WHERE { ?entity rdf:type <%s> }
                LIMIT 10000
                OFFSET %i
                """ % (ontology_label,len(instances))
            #print query
            if log:
                print('Querying dbpedia for',ontology_label,' OFFSET=',len(instances), file=sys.stderr)
                
            results = self.__my_query(query)
            if len(results) == 0:
                keep_searching = False
            else:
                for r in results:
                    instances.append(r['entity']['value'])
        return instances
    

    def query_dbpedia_for_dblink(self, dblink):
        """
        Returns a dictionary with all the triple relations stored in DBPEDIA for the given entity
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: dictionary with triples
        @rtype: dict
        """
        query = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?predicate ?object
                WHERE { <%s> ?predicate ?object }
                """ % dblink
        results = self.__my_query(query)
        return results

    def get_wiki_page_url_for_dblink(self,dblink):
        """
        Returns the wikipedia page url for the given DBpedia link (the relation 'http://xmlns.com/foaf/0.1/isPrimaryTopicOf is checked)
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: the wikipedia URL
        @rtype: str
        """
        
        dbpedia_json = self.query_dbpedia_for_dblink(dblink)
        lang = wikipage = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object    = dictionary['object']['value']
            
            if predicate == 'http://xmlns.com/foaf/0.1/isPrimaryTopicOf':
                wikipage = object
                break
            
        return wikipage

    def get_wiki_page_id_for_dblink(self, dblink):
        """
        Returns the wikipedia page id for the given DBpedia link (the relation http://dbpedia.org/ontology/wikiPageID is checked)
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: the wikipedia identifier
        @rtype: str
        """
        
        dbpedia_json = self.query_dbpedia_for_dblink(dblink)
        lang = wikipageid = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object    = dictionary['object']['value']
            
            if predicate == 'http://dbpedia.org/ontology/wikiPageID':
                wikipageid = object
                break
                
        return wikipageid
    
    def get_language_for_dblink(self, dblink):
        """
        Returns the language given a DBpedia link (xml:lang predicate)
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: the language (or None if there is no lang)
        @rtype: str
        """
        dbpedia_json = self.query_dbpedia_for_dblink(dblink)
        lang =  None
        for dictionary in dbpedia_json:
            if 'xml:lang' in dictionary['object']:
                lang = dictionary['object']['xml:lang']
                break
        return lang
    
    def get_wordnet_type_for_dblink(self, dblink):
        """
        Returns the wordnet type for the given DBpedia link (the relation http://dbpedia.org/property/wordnet_type is checked)
        It returns the last part of the WN type ((from http://www.w3.org/2006/03/wn/wn20/instances/synset-actor-noun-1 --> synset-actor-noun-1 )
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: the wordnet type
        @rtype: str
        """
        dbpedia_json = self.query_dbpedia_for_dblink(dblink)
        wordnet_type = None
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object    = dictionary['object']['value']
            
            if predicate == 'http://dbpedia.org/property/wordnet_type':
                wordnet_type = object.split('/')[-1]    # http://www.w3.org/2006/03/wn/wn20/instances/synset-actor-noun-1
                break
            
        return wordnet_type
    
    def is_person(self, dblink):
        """
        Returns True if the link has rdf:type dbpedia:Person, False otherwise
        @param dblink" a dbpedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: whether the dblink is a dbpedia person
        @rtype: str
        """
        dbpedia_json = self.query_dbpedia_for_dblink(dblink)
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object = dictionary['object']['value']
            
            if predicate == 'rdf:type' and object == 'http://dbpedia.org/ontology/person':
                return True
        return False

    def get_dbpedia_ontology_labels_for_dblink(self, dblink):
        """
        Returns the DBpedia ontology labels for the given DBpedia link (the type http://www.w3.org/1999/02/22-rdf-syntax-ns#type will be checked
        and only labels containing  http://dbpedia.org/ontology/* will be returned
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: list of ontology labels
        @rtype: list
        """

        dbpedia_json = self.query_dbpedia_for_dblink(dblink)

        ontology_labels = []
        for dictionary in dbpedia_json:
            predicate = dictionary['predicate']['value']
            object    = dictionary['object']['value']
            if 'rdf-syntax-ns#type' in predicate and 'http://dbpedia.org/ontology/' in object:
                ontology_labels.append(object)
        return ontology_labels    
    
    def query_dbpedia_for_unique_dblink(self, dblink):
        """
        Perform a check whether a dbpedia resource is unique
        @param dblink: a dbedia link (http://dbpedia.org/resource/Tom_Cruise)
        @type dblink: str
        @return: dictionary with triples
        @rtype: dict
        """
        query = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?predicate ?object
                WHERE { <%s> ?predicate ?object . FILTER NOT EXISTS { <%s> <http://dbpedia.org/ontology/wikiPageDisambiguates> ?o } }
                """ % (dblink, dblink)
        results = self.__my_query(query)
        return results
