import requests
import json
import base64
# 首先将图片读入
# 由于要发送json，所以需要对byte进行str解码
def send_massage(message):
    def getByte(path):
        with open(path, 'rb') as f:
            img_byte = base64.b64encode(f.read())
        img_str = img_byte.decode('ascii')
        return img_str


    img_str = getByte(message['path'])

    people = message['people']
    url = 'http://47.102.87.15:8888/warn'
    data = {'peoples': people, 'image': img_str}
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    json_mod = json.dumps(data)
    res = requests.post(url=url, data=json_mod, headers=headers)
    print(res.text)
    print(res.status_code)

    # 如果服务器没有报错，传回json格式数据
    print(eval(res.text))