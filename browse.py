from Libs.bottle import route, run, static_file
from settings import output, port


@route('<filename:path>')
def server_static(filename):

    if filename == '/':
        filename = '/index.html'
    return static_file(filename, root=output)


if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:"+str(port))
    run(host='0.0.0.0', port=port)

