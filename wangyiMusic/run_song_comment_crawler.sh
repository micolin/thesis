#!/bin/bash
INPUT_FILE='/home/micolin/thesis/data/song_id/song_id_'
LOG_FILE='log.song_comment_'
CRAWLED_FILE='/home/micolin/thesis/data/song_comment_old/song_comment_'
OUTPUT_FILE='/home/micolin/thesis/data/song_comment/song_commen_'
for ((idx=0; idx<12; idx++))
do
	#			    input		logfile		  crawled_file			outputfile
	python song_comment_crawler.py ${INPUT_FILE}${idx} ${LOG_FILE}${idx} ${CRAWLED_FILE}${idx} > ${OUTPUT_FILE}${idx} &
done
