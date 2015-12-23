# coding=utf-8
# 要爬取的网站url
main_url = 'http://139.129.8.188/'

# 设置代理
proxies = {
    "http": "127.0.0.1:1080",
    "https": "127.0.0.1:1080",
}
# 代理格式:
# {
#     "http": "127.0.0.1:1080",
#     "https": "127.0.0.1:1080",
# }

# HTTP请求的header
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
}

# 输出镜像文件的路径，最后要加 '/'
output = './output/'

# 日志及爬虫进度存储目录，最后要加 '/'
logs_path = './logs/'

# 每次请求的最大超时时间
request_timeout = 100

# 爬取页面的协程数
doc_pool_max = 20

# 爬取资源文件的协程数
res_pool_max = 20

# 每次请求随机延迟的时间，单位s，[最大值,最小值]
wait_time = [1, 3]

# 是否爬取该站以外的URL
outsite_page = False

# 爬取页面的深度，从0开始计，爬到第N层为止，-1表示无限制
recursion_deep = -1

# 请求资源文件出错最大重试次数（超时也算出错）
source_error_max = 20

# 请求页面出错最大重试次数（超时也算出错）
document_error_max = 40
# ------------------------------- #

# 本地浏览端口号
port = 12332
