#!/bin/bash

folder=.dbpedia_cache
n=`ls -1 $folder/* | wc -l | cut -d' ' -f1`
echo $n files cached removed
rm -rf $folder
