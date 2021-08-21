#!/bin/bash

# 장비명과 인터페이스 id 를 각각 읽어와 ai_modeling.py 에 적용
# ex) ai_modeling.py EXE030 10242 2021-08-15

today=$(date "+%Y%m%d")

TEMP=$(exec mysql -u *** -p****** AI -N -s -e "show tables where Tables_in_AI not LIKE '%predict%';")
for i in $TEMP; do
TEMP3="select itemid from AI.\`$i\` where key_ not LIKE '%CRC%' and key_ not LIKE '%speed%' group by itemid;"
RESULT=$(exec mysql -u *** -p****** AI -N -s -e "${TEMP3}")
for j in $RESULT; do
echo "ai $i $j $today"
python3 /home/guro/ai_modeling6.py $i $j $today
done
done
