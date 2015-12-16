# coding=utf-8
# 要爬取的网站url
main_url = 'http://www.liaoxuefeng.com/'

# 设置代理
proxies = None
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

# 每次请求的最大超时时间
request_timeout = 100

# 爬取页面的协程数
doc_pool_max = 2

# 爬取资源文件的协程数
res_pool_max = 2

# 每次请求随机延迟的时间，单位s，[最大值,最小值]
wait_time = [1, 3]

# 是否爬取该站以外的URL
outsite_page = False

# 爬取页面的深度，从0开始计，爬到第N层为止
recursion_deep = 1

# ------------------------------- #

# 本地浏览端口号
port = 12332
