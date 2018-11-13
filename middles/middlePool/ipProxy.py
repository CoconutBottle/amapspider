from settings import *
ipRandom = {"https":"14.17.121.132:12138",
            "http":"14.17.121.132:12138"} if IsDebug else ipProxy

if __name__ == '__main__':
    print(ipRandom)