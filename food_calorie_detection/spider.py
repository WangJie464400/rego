import requests

# 接口地址
url = 'http://localhost:8000/api/detect'

# 要上传的文件路径
file_path = rf'C:\Users\WJ-YYDS\Desktop\horses.jpg'  # 替换为您的图片路径

# 打开文件并准备提交
with open(file_path, 'rb') as f:
    files = {'file': f}
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()  # 如果响应状态码不是200，将引发异常
        # 打印响应内容
        print('状态码:', response.status_code)
        print('响应内容:', response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP错误发生: {http_err}')
        if response.content:
            print('错误详情:', response.json())
    except Exception as err:
        print(f'其他错误发生: {err}')