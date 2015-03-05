#!/bash

# 1) Sparql wrapper
python -c 'import SPARQLWrapper' 2> /dev/null

if [ "$?" -eq "1" ];
then
  echo 'SPARQLWrapper not installed'
  pip install --user SPARQLWrapper
else
  echo 'SPARQLWrapper is installed, so we skip this step'
fi


## 2) Dbpedia ontology 
mkdir resources 2>/dev/null
cd resources
URL='http://downloads.dbpedia.org/2014/dbpedia_2014.owl.bz2'
owl_name_bz2=`basename $URL`
wget $URL
bunzip2 $owl_name_bz2
echo "OWL_FILE = \"$owl_name_bz2\"[:-4]" > __init__.py
cd ..




