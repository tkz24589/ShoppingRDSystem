import time


def time_reckon(start_time, max_time):
    now_time = time.time()
    mul_time = now_time - start_time
    print('等待waring:%d' % mul_time)
    if mul_time > max_time:
        print("发送")
        return True
    else:
        return False
