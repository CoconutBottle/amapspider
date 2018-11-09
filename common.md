[TOC]


# 爬取高德项目 AmapSpider
**SEED_URL**

	http://report.amap.com/index.do
	http://report.amap.com/congest.do#

**GET获取城市code接口:** *[http://report.amap.com/ajax/getCityInfo.do?](http://report.amap.com/ajax/getCityInfo.do? "http://report.amap.com/ajax/getCityInfo.do?")*

**GET高德Traffice Report:**[http://report.amap.com/ajax/getQuarterReport.do](http://report.amap.com/ajax/getQuarterReport.do "http://report.amap.com/ajax/getQuarterReport.do")

**GETAmapGetCityRank:**[http://report.amap.com/ajax/getCityRank.do](http://report.amap.com/ajax/getCityRank.do "http://report.amap.com/ajax/getCityRank.do")
	
	Node:
	1. 中国主要城市拥堵排名(TOP100)
	2. 拥堵延时指数
	2. 周环比数
	2. 平均速度
	2. 畅通速度
	Obj：
	3.	1:2:城市名

**GET交通拥堵延时指数**

1.近七天：[http://report.amap.com/ajax/cityDaily.do?cityCode=441800](http://report.amap.com/ajax/cityDaily.do?cityCode=441800 "http://report.amap.com/ajax/cityDaily.do?cityCode=441800") <br>
2. 近24小时：[http://report.amap.com/ajax/cityHourly.do?cityCode=441800](http://report.amap.com/ajax/cityHourly.do?cityCode=441800 "http://report.amap.com/ajax/cityHourly.do?cityCode=441800")
	
	requestsParameters:	cityCode
	frequence: 1. D
			   2. H
			
**拥堵排名**

1. 区域：[http://report.amap.com/ajax/districtRank.do?linksType=1&cityCode=441800](http://report.amap.com/ajax/districtRank.do?linksType=1&cityCode=441800 "http://report.amap.com/ajax/districtRank.do?linksType=1&cityCode=441800")<br>
2. 商圈：
> To be continue

# 中华人民共和国自然资源部


# 易车指数
**SEED_URL**

	POST: http://index.bitauto.com/yicheindexpublic/rank/car-level
	{"id":4} 获取车系 code

	POST:http://index.bitauto.com/ai/v4/searchparam/getCompeteCarsPublic
	{"subject":"serial","id":"carmodel_2370","searchName":"","from":"search"} 获取车型 code 

	

## 易车报告
> http://index.bitauto.com/public/home/special

## 易车排行

> http://index.bitauto.com/yicheindexpublic/rank/list

+ D POST:{"id":4,"value":"brand"} 形式Payload value可变
	- 节点名称：
		+ 品牌 
			- 易车指数
			- 环比涨幅
		+ 车系名称
			- 易车指数
			- 环比涨幅
+ M POST: 请求参数 {"id":5,"value":"newEnergy"} 形式Payload value可变
	- 节点名称：
		+ 车系名称
			- 情感指数
			- 环比涨幅
+ M POST: 请求参数 {"id":6,"value":"brand"} 形式Payload value可变
	- 节点名称：
		+ 品牌
			- 销量（辆）
			- 环比涨幅
		+ 车系名称
			- 销量（辆）
			- 环比涨幅
+ D POST:http://index.bitauto.com/yicheindexpublic/indextrend（先POST-lastDate:{"model":"rank-index","date":"2017-12-27","timeType":"day"}）
+ {"serial":[{"name":"朗逸","value":"carmodel_2370"},..],"timeType":"day","fromTime":"2018-11-01","toTime":"2018-11-08"}
	+ RequestParameters:	toTime， fromTime， name, carmodel
	+ 近60天指数分布
+ M POST:http://index.bitauto.com/yicheindexpublic/praisetrend (先POST-lastDate：{"model":"rank-koubei","date":"2017-12-27","timeType":"month"})
+ {"serial":[{"name":"朗逸","value":"carmodel_2370"},...],"timeType":"month","fromTime":"2018-04-15","toTime":"2018-10-15"}
	+ RequestParameters:	toTime， fromTime， name, carmodel
	+ 

## 市场大盘
### 汽车行业销量趋势 Month
**SEED_URL:**http://index.bitauto.com/yicheindexpublic/data/last-date <br>
{"model":"market","date":"2017-12-27","timeType":"month"} 形式Payload 不可变

+ M POST: http://index.bitauto.com/yicheindexpublic/sale/saleTrend  请求参数  形式Payload toTime可变

> {"timeType":"month","fromTime":"2018-04-15","toTime":"2018-09-15"}

	指标：销量:月份

### 级别细分市场 
#### 份额趋势
> http://index.bitauto.com/yicheindexpublic/sale/saleLevelBar

+ POST: {"timeType":"month","fromTime":"2018-04-15","toTime":"2018-09-15"} 形式Payload toTime可变
	+ 节点名称
		+ 车型
			+ 月份
### 国别分布
#### 份额趋势
> http://index.bitauto.com/yicheindexpublic/sale/saleCountryByMonthLine

+ POST:{"timeType":"month","fromTime":"2018-04-15","toTime":"2018-09-15"} 形式Payload toTime可变
	+ 节点名称
		+ 国家
			+ 月份
