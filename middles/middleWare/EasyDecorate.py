#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)



from middles.middleAssist import logAsisst
from functools import wraps



def try_except(f):
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(e)

    return wrap

def try_except_callself(f):
    import time
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            print("sleep 300 sec!")
            time.sleep(300)
            return f(*args, **kwargs)

    return wrap

def tryexcept(logname):
    def func_wrapper(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            try:
                loger = logAsisst.imLog(filename=logname)()
                func(*args, **kwargs)
            except Exception as e:
                loger.error(e)

        return return_wrapper
    return func_wrapper




@tryexcept("testtest")
def test(e = "test"):
    print(e)
    raise ValueError("ddd")


if __name__ == '__main__':
    test()
