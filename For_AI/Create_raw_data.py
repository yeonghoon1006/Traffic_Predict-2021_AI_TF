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

# zabbix 에 쌓이는 데이터 파싱
sql = "select items.itemid, items.key_, items.hostid, hosts.host, history_uint.clock, history_uint.value from items JOIN hosts ON hosts.hostid = items.hostid JOIN history_uint ON history_uint.itemid = items.itemid where history_uint.clock < '"+str(timestamp)+"' and history_uint.clock >='"+str(timestamp-60)+"' and hosts.host NOT IN ('Zabbix server');"

cursor.execute(sql)
result = cursor.fetchall()

# zabbix 에서 필요한 data 만 AI DB 에 ISNERT

for row in result:
	sql2 = "insert into raw_data(itemid,key_,hostid,host,clock,value,day,holiday) values ('"+str(row[0])+"','"+row[1]+"','"+str(row[2])+"','"+row[3]+"','"+str(row[4])+"','"+str(row[5])+"','"+str(yoil)+"','"+str(holiday)+"');"
	cursor_ai.execute(sql2)


zabbix_db.commit()
zabbix_db.close()
ai_db.commit()
ai_db.close()
