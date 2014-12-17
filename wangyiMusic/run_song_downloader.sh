#!/bin/bash
INPUT_FILE='./data/song_id/song_id_'
GET_METHOD='from_idfile'
LOG_FILE='log.song_info_with_id_'
OUTPUT_FILE='./data/song_info/song_info_'
for ((idx=0; idx<12; idx++))
do 
	#							input_file				get_method		log_file						output_file
	python song_downloader.py 	${INPUT_FILE}${idx} 	${GET_METHOD}	${LOG_FILE}${idx}	>	${OUTPUT_FILE}${idx} &
done 
