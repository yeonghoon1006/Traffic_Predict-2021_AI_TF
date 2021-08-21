import pymysql
import datetime
import time

# 현재 날짜를 가져와 string 으로 변환
now=datetime.datetime.now()
now2 =now.strftime('%Y-%m-%d %H:%M:00')

# 1분 전 시간 계산 후, 연/월/일 변수로 저장 (자정이 지난 시간 계산을 위해)
before_one_minute = now - datetime.timedelta(minutes=1)
year = before_one_minute.strftime('%Y');
month = before_one_minute.strftime('%m');
day = before_one_minute.strftime('%d');

# 날짜를 요일로 변환
yoil=datetime.date(int(year),int(month),int(day)).weekday()

# 주말일 경우 holiday 를 1, 평일일 경우 holiday를 0, 2021년 공휴일 일 경우 holiday 를 1
# http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService 와 연동하여 요일을 가져올 수 있음 (횟수 제한)

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


# 현재 시간을 Unixtime으로 변환

dt=datetime.datetime.strptime(now2,'%Y-%m-%d %H:%M:%S')
timestamp = time.mktime(dt.timetuple())
#print(timestamp)

# Postgresql 에 연결

zabbix_db = pymysql.connect(host='localhost', user='guro', password='WkaWk*2!', db='zabbix', charset='utf8') 
ai_db = pymysql.connect(host='localhost', user='guro', password='WkaWk*2!', db='ai', charset='utf8')

cursor = zabbix_db.cursor()
cursor_ai = ai_db.cursor()

# zabbix database 에서 host(스위치,라우터) 목록 파싱
sql = "select host, hostid from hosts;"
cursor.execute(sql)
result = cursor.fetchall()

for row in result:
	host=str(row[0])
	hostid=str(row[1])
	
	# host 내역 중 원하는 host 만 추출, host 이름 = 테이블 이름 생성
	if 'Guro' in host and 'Templates' not in host and ('MEA' in host or 'MNP' in host or 'SEA' in host or 'MPC' in host or 'PET' in host or 'MVA' in host):
		sql = "create table if not exists `AI`.`"+host+"`(itemid bigint(20) unsigned, key_  varchar(255), clock int(11), value bigint(20) unsigned, yoil int, holiday int, PRIMARY KEY(itemid, clock));"
		cursor.execute(sql)		
		
		# host 에 맞는 item 추출
		sql = "select itemid, key_ from items where hostid="+hostid+";"
		cursor.execute(sql)
		result2 = cursor.fetchall()
		
		# item 에 5분 내에 쌓인 data를 AI Database 에 insert
		for row2 in result2:
			itemid=str(row2[0])
			key=str(row2[1])
			if '{#SNMPINDEX}' not in key and 'CRC' not in key:
				#print(hostid+"|"+str(row2[0])+"|"+str(row2[1]))
				sql="select clock,value from history_uint where itemid="+itemid+" and clock < '"+str(timestamp)+"' and clock >= '"+ str(timestamp-60)+"';"
				cursor.execute(sql)
				result3 = cursor.fetchall()
				for row3 in result3:
					clock=str(row3[0])
					value=str(row3[1])
					#print(host+"|"+hostid+"|"+itemid+"|"+key+"|"+clock+"|"+value+"|"+str(yoil)+"|"+str(holiday))
					sql2 = "insert into `"+host+"`(itemid,key_,clock,value,yoil,holiday) values ('"+itemid+"','"+key+"','"+clock+"','"+value+"','"+str(yoil)+"','"+str(holiday)+"');"
					cursor_ai.execute(sql2)
				


zabbix_db.commit()
zabbix_db.close()
ai_db.commit()
ai_db.close()
