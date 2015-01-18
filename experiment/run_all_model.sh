#!/bin/bash
SET_LEVEL=1k
TRAIN_PROB=0.7
E_TYPE='song'
TOP_N=200
RESULT_ROOT_DIR='./song_dataset/result_top'${TOP_N}

#Baseline
#python item_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/${SET_LEVEL}/itemCF_${SET_LEVEL}_${TRAIN_PROB} &
#python user_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/${SET_LEVEL}/userCF_${SET_LEVEL}_${TRAIN_PROB} &

#MyMethod
#python item_tag_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N > ${RESULT_ROOT_DIR}/${SET_LEVEL}/itemTagCF_${SET_LEVEL}_${TRAIN_PROB} &
python user_tag_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N > ${RESULT_ROOT_DIR}/${SET_LEVEL}/userTagCF_${SET_LEVEL}_${TRAIN_PROB} &
#python userLDA.py $SET_LEVEL $TRAIN_PROB 200 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/${SET_LEVEL}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_200topic &
#python userLDA.py $SET_LEVEL $TRAIN_PROB 2000 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/${SET_LEVEL}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_2000topic &
#python userLDA.py $SET_LEVEL $TRAIN_PROB 1000 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_1000topic &
#python userLDA.py $SET_LEVEL $TRAIN_PROB 1500 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/${SET_LEVEL}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_1500topic &
python hybirdModel.py $SET_LEVEL $TRAIN_PROB 1500 $TOP_N mix_sim > ${RESULT_ROOT_DIR}/${SET_LEVEL}/hybirdModel_${SET_LEVEL}_${TRAIN_PROB}_mix_sim &
python hybirdModel.py $SET_LEVEL $TRAIN_PROB 1500 $TOP_N mix_result > ${RESULT_ROOT_DIR}/${SET_LEVEL}/hybirdModel_${SET_LEVEL}_${TRAIN_PROB}_mix_result &
