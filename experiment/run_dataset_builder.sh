#!/bin/bash
sample_num=10000
output_file='./song_dataset/user_dataset_1w_4'
input_file='../wangyiMusic/data/user_info/user_id_all'
python dataset_builder.py build_dataset $input_file $sample_num song > $output_file

train_prob=0.7
python dataset_builder.py split_dataset $output_file $train_prob
