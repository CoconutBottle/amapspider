##IF LOCALHOST RUN THIS PROGRAM
##IT WILL BE CHANGED MYSQL'S CONNECTION ADDRESS
IsDebug = True


##RedisHOST PASSWORD AND PORT
RedisHost = {
    "host": "10.1.0.253" if IsDebug else "10.0.0.7",
    "port": 6400 if IsDebug else 7777,
    "passwd": "",
    "db": 2 if IsDebug else 2
}
##MysqlHOST PASSWORD AND PORT
MysqlHost = {
    "host": "10.1.0.253" if IsDebug else "10.1.1.186",
    "port": 3401 if IsDebug else 3600,
    "user": "root",
    "passwd": "iimedia",
    "db": "shujubaogao" if IsDebug else "iimedia_data"
}

SsdbHost = {
    "host": "10.1.0.253" if IsDebug else "10.0.0.14",
    "port": 8888 if IsDebug else 7779,
}

##PRoxyIp
ipProxy = {
    "https":"14.17.121.132:12138",
    "http":"14.17.121.132:12138"
}
