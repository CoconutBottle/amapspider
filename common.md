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
