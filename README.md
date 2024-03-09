# php2wsgi
A PHP wrapper for WSGI -- run WSGI python apps on a plain PHP webhost.

My web host, Dreamhost, recently disabled WSGI application support on shared hosting, directing people to their premium VPS service. I only have a few tiny Python apps written in Bottle (even smaller than Flask), and I'm not about to janitor a VM just for that. Instead, I built something mildly unholy -- a PHP+Python wrapper to run any WSGI application on a plain Apache+PHP stack. Relies on .htaccess URL rewriting, and assumes that these files plus the application are all sitting in the document root of a given web server.

## Deploying
To use, deploy these files into the document root of an Apache web server that has PHP enabled. Remove the demo.py and modify wsgi-host.py where the comment says "CONFIGURE THIS TO IMPORT YOUR APPLICATION".
If all goes well, visiting that web server should show you your app.

If all does not go well, you can turn on debug output in both wrap.php (which gets the requests, translates it into a WSGI execution, and gathers the results) and in wsgi-host.py (which actually runs the python part). 

## Known issues
 - This is just tested well enough to run my little apps. I can't guarantee it will work in all cases.
 - HTTP POST operations are read into memory during handoff, so don't use this for apps that do large HTTP operations such as big file uploads.
 - No warranty.
