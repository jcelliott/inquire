#!/usr/bin/env bash
# setup for question answering app

# start Stanford NER server
docker run -d -p 9090:8080 jcelliott/ner
