#!/usr/bin/env bash
# setup for question answering app

# start Stanford NER server
_ner_dir='resources/stanford-ner'
java -mx700m -cp "$_ner_dir/stanford-ner.jar" edu.stanford.nlp.ie.NERServer \
  -loadClassifier "$_ner_dir/classifiers/english.muc.7class.distsim.crf.ser.gz" \
  -port 9090 \
  -outputFormat inlineXML
