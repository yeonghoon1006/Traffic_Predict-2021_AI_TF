<HTML>
<HEAD>
<TITLE> AI 감시 화면 </TITLE>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<script type="text/javascript" src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/modules/exporting.js"></script>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<link rel="stylesheet" type="text/css" href="ai_ui_style.css">
</HEAD>


<?php
//그래프를 그리기 위한 데이터 파싱

//mysql 연결
$db = mysqli_connect('localhost','zabbix','WkaWk*2!','AI');
// 쿼리문(Guro-MNP149K 의 32257/32255-TOTAL UP/DOWN TRAFFIC 정보)
$sql = "select from_unixtime(clock) as time,value/1000/1000/1000 as value from `Guro-MNP149K` where itemid='32257' order by clock desc limit 720;";
//결과를 변수에 할당
$result = mysqli_query($db,$sql);
//배열에 출력된 배열을 담기(모든 데이터)

while($row=mysqli_fetch_assoc($result)){
$data_array[] = ($row);
}

$sql2 = "select from_unixtime(clock) as time,value/1000/1000/1000 as value2 from `Guro-MNP149K` where itemid='32255' order by clock desc limit 720;";
$result2 = mysqli_query($db,$sql2);

while($row2=mysqli_fetch_assoc($result2)){
$data_array2[] = ($row2);
}

// 두 쿼리문 결과를 Variable_temp 로 합쳐서 저장
$Variable_temp = [];
for($i=0; $i < count($data_array) ; $i++)
{
$temp = [];
$temp[time] = $data_array[$i][time];
$temp[value] =$data_array[$i][value];
$temp[value2] = $data_array2[$i][value2];
$Variable_temp[$i] = $temp;
}

//Json 으로 encode
$chart = json_encode($Variable_temp);

//쿼리문(Guro-MNP150G 의 32258/32259-TOTAL UP/DONW TRAFFIC 정보)
$sql3 = "select from_unixtime(clock) as time,value/1000/1000/1000 as value from `Guro-MNP150G` where itemid='32258' order by clock desc limit 720;";
//결과를 변수에 할당
$result3 = mysqli_query($db,$sql3);
//배열에 출력된 배열을 담기(모든 데이터)

while($row3=mysqli_fetch_assoc($result3)){
$data_array3[] = ($row3);
}

$sql4 = "select from_unixtime(clock) as time,value/1000/1000/1000 as value2 from `Guro-MNP150G` where itemid='32259' order by clock desc limit 720;";
$result4 = mysqli_query($db,$sql4);

while($row4=mysqli_fetch_assoc($result4)){
$data_array4[] = ($row4);
}

// 두 쿼리문 결과를 Variable_temp2 로 합쳐서 저장
$Variable_temp2 = [];
for($i=0; $i < count($data_array3) ; $i++)
{
$temp = [];
$temp[time] = $data_array3[$i][time];
$temp[value] =$data_array3[$i][value];
$temp[value2] = $data_array4[$i][value2];
$Variable_temp2[$i] = $temp;
}

//Json 으로 encode
$chart2 = json_encode($Variable_temp2);


//알람 발생 이력 TABLE 에 접근하여 미복구 알람 정보 파싱
$sql="SELECT * FROM ai_problem_detection";
$result = mysqli_query($db, $sql);
while ($row = mysqli_fetch_array($result)) {
    if($row[end_time] == "미복구"){
      $falut_flag=1;
      echo "미복구 장애 발견";
    }
  }
?>

<body id="background" class="contain1er">
<!-- 모니터링 아이콘 표시 / 클릭시 좌우 애니메이션 적용 및 알람 감시 테이블 표시-->
<div>
	<div id="move_click" class="container" > 
		<h2>
		  <span class="light" >INTERVIEW</span> 
		  <span>Monitoring...</span>  
		</h2>
		<svg  class="pulse" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" >
       			<circle id="Oval" cx="512" cy="512" r="512"></circle>
       		 	<circle id="Oval" cx="512" cy="512" r="512"></circle>
			<circle id="Oval" cx="512" cy="512" r="512"></circle>
			<circle id="Oval" cx="512" cy="512" r="512"></circle>
		</svg>
	</div>
	<!-- Table 영역 해민 구현-->
	
	<iframe id="monitor_table" src="table/index.php" width="90%" height="100%" align="right"> </iframe>
</div>

<!-- 그래프-그라파나/로그-DB/MAP-자빅스로 연동하는 아이콘 설정 -->
<img id="graph" src="./img/graph_icon.png" style="cursor:pointer" onclick="javascript:newin=window.open('about:blank'); newin.location.href='http://211.48.55.81:3000/d/7FZ3B7_Gk/home-dashboard?viewPanel=6&orgId=1&var-host=Guro-GOA126&var-key=total.traffic.in&refresh=1m';">
<img id="map" src="./img/map_icon.png" style="cursor:pointer" onclick="javascript:newin=window.open('about:blank'); newin.location.href='http://211.48.55.81/zabbix/zabbix.php?action=map.view&ddreset=1';">
<img id="log" src="./img/log_icon.png" style="cursor:pointer">


<script>
// 모니터링 아이콘 클릭 시 동작
var flag = 0;
		
$('#move_click').on('click',function(){
		
if ( flag == 0 ) {
				$('#move_click').animate({left:'0%',top:'0%',width:'18%',height:'36%'},500,"linear");
		        flag = 1;
		} else {
		        $('#move_click').animate({left:'0%',top:'0%',width:'100%',height:'100%'},500,"linear");
		        flag = 0;
}
});

</script>


<script>
// 구글차트 영역

google.charts.load('current', {'packages':['corechart', 'line']});
google.charts.setOnLoadCallback(drawChart);
google.charts.setOnLoadCallback(drawChart2);

function drawChart() {
// DATA 생성 - PHP JSON 변수 이용

var data = new google.visualization.DataTable();
data.addColumn('date', 'Date');
data.addColumn('number', 'DOWN');
data.addColumn('number', 'UP');

var js_array = <?php echo $chart?>; 

for (var i = 0; i < js_array.length; i++) {
var temp = js_array[i].time.split(' ');
var temp_date = temp[0].split('-');
var temp_time = temp[1].split(':');

js_array[i].value *=1;
js_array[i].value2 *=1;

data.addRows([[new Date(temp_date[0],temp_date[1],temp_date[2],temp_time[0],temp_time[1]), js_array[i].value,js_array[i].value2]]);
}

// 구글 차트 옵션 설정
var linearOptions = {
        title: 'Guro-MNP149K',

        backgroundColor : '#141619',
        legend: 'none',
        width: 965,
        height: 200,
        titleTextStyle: {color: '#ffffff'},
        chartArea: {'width': '90%', 'height': '80%'},
        hAxis: {
          textStyle: {color: '#ffffff'}, 
          gridlines: { color: '#141619'} 
        },
        vAxis: {
          textStyle: {color: '#ffffff'}, 
          gridlines: { color: '#4d4e4f'}, 
          //title: 'Population (millions)',
          ticks: [0, 25, 50, 75, 100]
        }
      };

      var linearChart = new google.visualization.LineChart(document.getElementById('linear_div'));
       linearChart.draw(data, linearOptions);

}

function drawChart2() {
// DATA 생성 - PHP JSON 변수 이용

var data = new google.visualization.DataTable();
data.addColumn('date', 'Date');
data.addColumn('number', 'DOWN');
data.addColumn('number', 'UP');

var js_array = <?php echo $chart2?>;

for (var i = 0; i < js_array.length; i++) {
var temp = js_array[i].time.split(' ');
var temp_date = temp[0].split('-');
var temp_time = temp[1].split(':');

js_array[i].value *=1;
js_array[i].value2 *=1;

data.addRows([[new Date(temp_date[0],temp_date[1],temp_date[2],temp_time[0],temp_time[1]), js_array[i].value,js_array[i].value2]]);
}

// 구글 차트 옵션 설정
var linearOptions = {
        title: 'Guro-MNP150G',
        backgroundColor : '#141619',
        legend: 'none',
        width: 965,
        height: 200,
        titleTextStyle: {color: '#ffffff'},
        chartArea: {'width': '90%', 'height': '80%'},
        
        hAxis: {
         
          textStyle: {color: '#ffffff'}, 
          gridlines: { color: '#141619'} 
          //title: 'Date'
        },
        vAxis: {
          textStyle: {color: '#ffffff'}, 
          gridlines: { color: '#4d4e4f'}, 
          //title: 'Population (millions)',
          ticks: [0, 25, 50, 75, 100]
        }
      };

      var linearChart = new google.visualization.LineChart(document.getElementById('linear_div2'));
       linearChart.draw(data, linearOptions);

}

</script>

<!-- 그래프 영역 -->
<div id="linear_div"></div>
<div id="linear_div2"></div>
</body>
