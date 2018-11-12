# 说明
	seed代表种子变量，定义与指标节点频道数据无直接联系，但对于获取其却必不可少的变量参数
	为种子参数;其变量名，函数名均带有seed.
	seed变量值均要以持久保存，其保存路径为SSDB或mysql

# Yiche频道节点指标json

	data:[｛ channel:string,
	   node:string,
	   haskid: bool
	   data:[
		{
		node:string,
		haskid:bool
		},
		{
	    node:string,
		haskid:bool
		}
		...]
	｝]
