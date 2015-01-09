#!bin/bash
SET_LEVEL=500
TRAIN_PROB=0.7
E_TYPE='song'
TOP_N=100
RESULT_ROOT_DIR='./song_dataset/result_top'${TOP_N}

#Baseline
python user_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/userCF_${SET_LEVEL}_${TRAIN_PROB} &
python item_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/itemCF_${SET_LEVEL}_${TRAIN_PROB} &

#MyMethod
python item_tag_CF.py $SET_LEVEL $TRAIN_PROB $TOP_N > ${RESULT_ROOT_DIR}/itemTagCF_${SET_LEVEL}_${TRAIN_PROB} &
python userLDA.py $SET_LEVEL $TRAIN_PROB 1000 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_1000topic &
python userLDA.py $SET_LEVEL $TRAIN_PROB 1500 $TOP_N $E_TYPE > ${RESULT_ROOT_DIR}/userLDA_${SET_LEVEL}_${TRAIN_PROB}_1500topic &
python hybirdModel.py $SET_LEVEL $TRAIN_PROB 1000 $TOP_N > ${RESULT_ROOT_DIR}/hybirdModel_${SET_LEVEL}_${TRAIN_PROB}_1000topic &
python hybirdModel.py $SET_LEVEL $TRAIN_PROB 1500 $TOP_N > ${RESULT_ROOT_DIR}/hybirdModel_${SET_LEVEL}_${TRAIN_PROB}_1500topic &
