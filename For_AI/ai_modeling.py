import pymysql
import datetime
import sys

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score
import xgboost as xgb

from sklearn.preprocessing import normalize

# 장비명(equip), interface 번호(inter), 날짜(date_in)을 변수로 받음
equip = sys.argv[1]
inter = sys.argv[2]
date_in = sys.argv[3]

# postgresql 의 AI database에 접속
ai_db = pymysql.connect(host='127.0.0.1', user='guro', password='WkaWk*2!', db='AI', charset='utf8')
cursor_ai = ai_db.cursor()

# 장비와 interface 에 맞는 key_(interface 명) 추출
sql = "select key_ from `AI`.`"+equip+"` where itemid="+str(inter)+" group by itemid;"
cursor_ai.execute(sql)
key = 0

# interace 명을 table 이름으로 설정하여 생성, _predict_rf(랜덤 포레스트)/_predict_xb(xgboost) 
for row in cursor_ai.fetchall():
	key = row[0]


sql = "create table if not exists `AI`.`"+equip+"_predict_rf`(itemid bigint(20) unsigned, key_  varchar(255), clock int(11), predict_value float, PRIMARY KEY(itemid, clock));"
cursor_ai.execute(sql)
sql = "create table if not exists `AI`.`"+equip+"_predict_xb`(itemid bigint(20) unsigned, key_  varchar(255), clock int(11), predict_value float, PRIMARY KEY(itemid, clock));"
cursor_ai.execute(sql)

# AI 모델링 하기 위한 데이터를 AI database 에서 가져와 dataframe 으로 저장
sql = "select CAST(from_unixtime(clock,'%Y%m%d') AS INT) as date, CAST(from_unixtime(clock,'%H%i') AS INT) as time,round(value/1000/1000/1000,2) as traffic,yoil,holiday from `"+str(equip)+"` where itemid='"+str(inter)+"' and CAST(from_unixtime(clock,'%Y%m%d') AS INT) < '"+str(date_in)+"';"
df = pd.read_sql_query(sql,ai_db)

# y값(종속변수)를 제외한 x값(독립 변수) 을 df_features 로 저장
df_features = df.drop('traffic',axis =1)
#print(df_features)

# Training/Test 데이터 셋으로 나눔
X_train, X_test, y_train, y_test = train_test_split(df_features, df['traffic'], train_size =0.75, test_size = 0.25, random_state=34)


# Random forest 학습
'''
################## Random forest ##############
forest = RandomForestRegressor(random_state=1) # 객체생성 
forest.fit(X_train, y_train) #훈련

# evaluate predictions
acc = forest.score(X_test, y_test) #훈련 정확도 측정 
#print('Accuracy: %.3f' % acc)

#############################################
'''

# Xgboost 학습
################# Xgboost ####################

xgb = xgb.XGBRegressor()
xgb.fit(X_train, y_train)

acc_xgb = xgb.score(X_test, y_test)
#print('Accuracy: %.3f' % acc_xgb)

############################################


# 내일 날짜(예측하고자 하는 날짜)
tomorrow = datetime.datetime.strptime(date_in,"%Y%m%d") + datetime.timedelta(days=1)

year = tomorrow.strftime('%Y')
month = tomorrow.strftime('%m')
day = tomorrow.strftime('%d')
predict_date=year+month+day

# 내일 요일/공휴일 설정
yoil=datetime.date(int(year),int(month),int(day)).weekday()
holiday=0;

if yoil == 5 or yoil == 6:
	holiday=1

if year == "2021":
		if month == "01":
				if day == "01":
						holiday=1
		if month == "02":
				if day == "11":
						holiday=1
				if day == "12":
						holiday=1
		if month == "03":
				if day == "01":
						holiday=1
		if month == "05":
				if day == "05":
						holiday=1
				if day == "19":
						holiday=1
		if month == "09":
				if day == "20":
						holiday=1
				if day == "21":
						holiday=1
				if day == "22":
						holiday=1

# Random Forest 를 이용하여 내일 데이터 traffic 을 예측
# 예측한 값을 _predict_rf Table 에 저장
'''
#RANDOM FOREST PREDICT
for hour in range(0,24):
	for min in range(0,60):
		if len(str(hour)) == 1:
			hour = '0' + str(hour)
		if len(str(min)) == 1:
			predict_time=str(hour)+'0'+str(min)
		else:
			predict_time=str(hour)+str(min)
		#print(str(predict_date)+' '+ str(predict_time),end=' ')
		unixtime = datetime.datetime.strptime(predict_date+predict_time+'00','%Y%m%d%H%M%S').timestamp()
		res=forest.predict(pd.DataFrame([[predict_date,predict_time,yoil,holiday]]))
		sql="insert into `AI`.`"+equip+"_predict_rf`(itemid,key_,clock,predict_value) values('"+inter+"','"+key+"','"+str(unixtime)+"','"+str(res[0])+"');"
		#print(sql)
		cursor_ai.execute(sql)

ai_db.commit()
'''

# Xgboost 를 이용하여 내일 데이터 traffic 을 예측
# 예측한 값을 _predict_xb Table 에 저장


for hour in range(0,24):
	for min in range(0,60):
		if len(str(hour)) == 1:
			hour = '0' + str(hour)
		if len(str(min)) == 1:
			predict_time=str(hour)+'0'+str(min)
		else:
			predict_time=str(hour)+str(min)
		#print(str(predict_date)+' '+ str(predict_time),end=' ')
		unixtime = datetime.datetime.strptime(predict_date+predict_time+'00','%Y%m%d%H%M%S').timestamp()
		res=xgb.predict(pd.DataFrame([[predict_date,predict_time,yoil,holiday]]))
		sql="insert into `AI`.`"+equip+"_predict_xb`(itemid,key_,clock,predict_value) values('"+inter+"','"+key+"','"+str(unixtime)+"','"+str(res[0])+"');"
		#print(sql)
		cursor_ai.execute(sql)

ai_db.commit()

""" 
확인 
cursor_ai.execute(sql)
result = cursor_ai.fetchall()

for row in result:
	print(str(row[0])+"	 |	"+str(row[1])+"	 |	"+str(row[2])+"	 |	"+str(row[3]) + "  | "+str(row[4])+"  |	 "+str(row[5]))


ai_db.commit()
"""

ai_db.close()