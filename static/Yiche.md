[TOC]

http://index.bitauto.com/public/home/rank
-------------------
# Seed_url 

	+ http://index.bitauto.com/yicheindexpublic/rank/car-level
		+ 获取车型
		+ 参数｛"id":4｝ id E 4 5 6 固定不变
		+ 获取字段： name, value
		
		
	+ http://index.bitauto.com/yicheindexpublic/data/last-date
		+ 获取该指标最近更新时间
		+ 参数(指数)：{"model":"rank-index","date":"2017-12-27","timeType":"day"} model E rank-index
		+ 参数（口碑）：{"model":"rank-koubei","date":"2017-12-27","timeType":"month"}
		+ 参数（市场大盘）：{"model":"market","date":"2017-12-27","timeType":"month"}
		+ 
	
	+ http://index.bitauto.com/ai/v4/searchparam/getCompeteCarsPublic
		+ {"subject":"serial","id":"carmodel_5426","searchName":"","from":"search"} 固定不变

---------------------
# 指标url
## 市场大盘

	+ http://index.bitauto.com/yicheindexpublic/sale/saleTrend
		+ 获取月度销量  辆
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime
		+ 获取字段：yAxis.name, xAxis.data, series.data
		+ 频率 每月
	
	+ http://index.bitauto.com/yicheindexpublic/sale/saleCountryByMonthLine
		+ 获取月度国家份额趋势   %
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime
		+ 获取字段：xAxis.name，series.data， yAxis.name
		+ 频率 每月
	+ http://index.bitauto.com/yicheindexpublic/sale/saleLevelBar
		+ 获取车型市场份额 %
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime
		+ 获取字段：xAxis.name，series.data， yAxis.name
		+ 频率 每月
	

<br>

	+ http://index.bitauto.com/yicheindexpublic/sale/saleDynamicBar
		+ 获取汽车动力类型 %
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime， fromTime
		+ 获取字段：yAxis.name， series.data
		+ 建议季度

	+ http://index.bitauto.com/yicheindexpublic/sale/saleMakeBar
		+ 获取厂商份额 %
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime， fromTime
		+ 获取字段：yAxis.name， series.name
		+ 建议季度
		
	+ http://index.bitauto.com/yicheindexpublic/sale/saleLevelBubule
		+ 获取车型细分市场份额
		+ 参数{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime， fromTime
		+ 获取字段series.data
		+ 建议月

	+ http://index.bitauto.com/yicheindexpublic/sale/saleCountryPie
		+ 获取国别分布
		+ 参数：{"timeType":"month","fromTime":"2017-10-15","toTime":"2018-09-15"} toTime， fromTime
		+ 获取字段：series.data
		+ 建议半年季度


## 易车排行
	
+ http://index.bitauto.com/yicheindexpublic/indextrend
	+ 获取易车指数排行
	+ 参数{"serial":[{"name":"LAFESTA 菲斯塔","value":"carmodel_5426"},...],"timeType":"day","fromTime":"2018-11-05","toTime":"2018-11-12"}`
	+ 获取字段xAxis.data, series.data   
	+ value 特定， name 任意

+ http://index.bitauto.com/yicheindexpublic/praisetrend
	+ 获取易车口碑
	+ 参数{"serial":[{"name":"LAFESTA 菲斯塔","value":"carmodel_5426"},...],"timeType":"month","fromTime":"2018-11-05","toTime":"2018-11-12"}`
	+ 获取字段xAxis.data, series.data   
	+ value 特定， name 任意


+ http://index.bitauto.com/yicheindexpublic/rank/list
	+ 获取销量排名
	+ {"id":6,"value":"allModelLevel"}，{"id":6,"value":"brand"}，{"id":6,"value":"xxx"} id不可变， value可变
