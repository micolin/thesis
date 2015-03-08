#!/bin/bash
TRAIN_PROB=0.7
E_TYPE='song'
TOPIC_NUM=1500

for set_level in "1w"
do 
	#####################
	#>>>>---Baseline--<<<<
	#####################
	#python random_select.py $set_level $TRAIN_PROB $E_TYPE > ./song_dataset/result_more/rs_${set_level}_${TRAIN_PROB} 
	#python popularity.py $set_level $TRAIN_PROB $E_TYPE > ./song_dataset/result_more/pop_${set_level}_${TRAIN_PROB}

	for top_n in "5"
	do
		RESULT_ROOT_DIR='./song_dataset/result_top'${top_n}
		if [ ! -d ${RESULT_ROOT_DIR} ]
		then
			mkdir $RESULT_ROOT_DIR
		fi

		OUTPUT_DIR=${RESULT_ROOT_DIR}'/'${set_level}
		if [ ! -d ${OUTPUT_DIR} ]
		then
			mkdir $OUTPUT_DIR
		fi
		#####################
		#>>>>---Baseline--<<<<
		#####################
		#python item_CF.py $set_level $TRAIN_PROB $top_n $E_TYPE > ${RESULT_ROOT_DIR}/${set_level}/itemCF_${set_level}_${TRAIN_PROB} 
		#python user_CF.py $set_level $TRAIN_PROB $top_n $E_TYPE > ${RESULT_ROOT_DIR}/${set_level}/userCF_${set_level}_${TRAIN_PROB} 

		#####################
		#>>>>---SingleModel--<<<<
		#####################
		#python item_tag_CF.py $set_level $TRAIN_PROB $top_n > ${RESULT_ROOT_DIR}/${set_level}/itemTagCF_${set_level}_${TRAIN_PROB}
		#python user_tag_CF.py $set_level $TRAIN_PROB $top_n > ${RESULT_ROOT_DIR}/${set_level}/userTagCF_${set_level}_${TRAIN_PROB}
		#python userLDA.py $set_level $TRAIN_PROB $TOPIC_NUM $top_n $E_TYPE > ${RESULT_ROOT_DIR}/${set_level}/userLDA_${set_level}_${TRAIN_PROB}_${TOPIC_NUM}topic

		#####################
		#>>>>---HybirdModel--<<<<
		#####################
		for recommend_job in "mix_sim" "mix_sim_reorder"
		do
			python hybirdModel.py $set_level $TRAIN_PROB $TOPIC_NUM $top_n $recommend_job > ${RESULT_ROOT_DIR}/${set_level}/new/hybirdModel_${set_level}_${TRAIN_PROB}_${recommend_job}
			
			python ubase_hybirdModel.py $set_level $TRAIN_PROB 'tag' $recommend_job $top_n > ${RESULT_ROOT_DIR}/${set_level}/new/ub_hybird_tag_${set_level}_${TRAIN_PROB}_${recommend_job}

			python ubase_hybirdModel.py $set_level $TRAIN_PROB 'lda' $recommend_job $top_n $TOPIC_NUM > ${RESULT_ROOT_DIR}/${set_level}/new/ub_hybird_lda_${set_level}_${TRAIN_PROB}_${recommend_job}
			#python ubase_hybirdModel.py $set_level $TRAIN_PROB 'lda' $recommend_job $top_n $TOPIC_NUM
		done
	done
done
