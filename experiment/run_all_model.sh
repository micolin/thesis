#!/bin/bash
TRAIN_PROB=0.7
E_TYPE='song'
TOPIC_NUM=3000

for set_level in "1w"
do 
	RESULT_ROOT_DIR='./rec_result/'${set_level}
	if [ ! -d ${RESULT_ROOT_DIR} ]
	then
		mkdir $RESULT_ROOT_DIR
	fi

	#####################
	#>>>>---Baseline--<<<<
	#####################
	#python random_select.py $set_level $TRAIN_PROB > ${RESULT_ROOT_DIR}/rs_${set_level}_${TRAIN_PROB} 
	#python popularity.py $set_level $TRAIN_PROB > ${RESULT_ROOT_DIR}/pop_${set_level}_${TRAIN_PROB}

	for user_k in "20" "50"
	do

		#####################
		#>>>>---Baseline--<<<<
		#####################
		#python item_CF.py $set_level $TRAIN_PROB $top_n $E_TYPE > ${RESULT_ROOT_DIR}/${set_level}/itemCF_${set_level}_${TRAIN_PROB} 
		#python user_CF.py $set_level $TRAIN_PROB $user_k > ${RESULT_ROOT_DIR}/userCF_${set_level}_${TRAIN_PROB}_${user_k} 

		#####################
		#>>>>---SingleModel--<<<<
		#####################
		#python item_tag_CF.py $set_level $TRAIN_PROB $top_n > ${RESULT_ROOT_DIR}/${set_level}/itemTagCF_${set_level}_${TRAIN_PROB}
		#python user_tag_CF.py $set_level $TRAIN_PROB $user_k > ${RESULT_ROOT_DIR}/userTagCF_${set_level}_${TRAIN_PROB}_${user_k}
		#python userLDA.py $set_level $TRAIN_PROB $TOPIC_NUM $user_k > ${RESULT_ROOT_DIR}/userLDA_${set_level}_${TRAIN_PROB}_${TOPIC_NUM}_${user_k}

		#####################
		#>>>>---HybirdModel--<<<<
		#####################
		for recommend_job in "mix_sim" "mix_sim_reorder"
		do
			#python hybirdModel.py $set_level $TRAIN_PROB $TOPIC_NUM $recommend_job $user_k > ${RESULT_ROOT_DIR}/hybirdModel_${recommend_job}_${set_level}_${TRAIN_PROB}_${TOPIC_NUM}_${user_k}
			
			python ubase_hybirdModel.py $set_level $TRAIN_PROB 'tag' $recommend_job $user_k 500 > ${RESULT_ROOT_DIR}/ubhybird_tag_${recommend_job}_plus_0.8_${set_level}_${TRAIN_PROB}_${user_k}

			#python ubase_hybirdModel.py $set_level $TRAIN_PROB 'lda' $recommend_job $user_k 500 $TOPIC_NUM > ${RESULT_ROOT_DIR}/ubhybird_lda_${recommend_job}_plus_0.9_${set_level}_${TRAIN_PROB}_${TOPIC_NUM}_${user_k}
		done
	done
done
