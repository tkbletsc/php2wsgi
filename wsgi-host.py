from io import BytesIO
import sys,os,re
import json

from demo import application as app
# ^^ this line needs to be updated to import *your* application as "app"
# if you have "demo.py" that has at the app variable called "application", then you'd do:
#   from demo import application as app

# set to true to get a LOT of debug info about the environment
DEBUG=False

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def call_application(app, environ):
    status = None
    headers = None
    body = BytesIO()
    
    def start_response(rstatus, rheaders):
        nonlocal status, headers
        status, headers = rstatus, rheaders
        
    app_iter = app(environ, start_response)
    try:
        for data in app_iter:
            assert status is not None and headers is not None, \
                "start_response() was not called"
            body.write(data)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
    return status, headers, body.getvalue()

def wrap_wsgi(app):
    # defaults
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': sys.stdin.buffer,
        'wsgi.errors': BytesIO(),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
        'QUERY_STRING': '',  # Add any query parameters if needed
        'HTTP_ACCEPT': 'text/html',
        'HTTP_USER_AGENT': 'Your User Agent',
        # Add more environment variables as needed for your application
    }

    dprint("<hr>")
    dprint(f"orig env: {environ}")
    dprint("<hr>")
    # override with the json of key values pairs in argv[1] if present
    if len(sys.argv)>=2:
        env_new_json = sys.argv[1]
        env_new = json.loads(env_new_json)
        dprint(f"env addons from argv: {env_new}")
        environ.update(env_new)
        dprint(f"new env: ")
        dprint('<br>\n'.join(str(k)+'='+str(v) for k,v in environ.items()))
        
    dprint("<hr>")
    status, headers, body = call_application(app, environ)
    dprint("<hr>")
    dprint("status", status)
    dprint("<hr>")
    dprint("headers", headers)
    dprint("<hr>")
    sys.stdout.flush()
    
    sys.stdout.buffer.write(body)
    
    # we emit the status and headers via a special file dsecriptor #3 which was set up for us by the calling wrap.php
    # format is a json with the status code (e.g. 200), status message (e.g. "OK"), and dictionary of HTTP headers
    fd3 = os.fdopen(3, 'w')
    status_code,status_msg = re.split(r'\s', status, 1)
    fd3.write(json.dumps([status_code,status_msg,dict(headers)]))
    fd3.close()
    
if __name__ == '__main__':
    wrap_wsgi(app)
