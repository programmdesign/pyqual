import os
try:
    import cherrypy
    nocherry = False
except ImportError:
    nocherry = True

VERSION = '1.0.5'

# Control database connection settings
DB_HOST = 'localhost'
DB_NAME = 'pyqual'
DB_USER = 'pyqual'
DB_PASS = ''
DB_PORT = 5432
DSN = "dbname=%s user=%s password=%s port=%s host=%s" % (DB_NAME, DB_USER, DB_PASS, DB_PORT, DB_HOST)

# Web interface IP and port to bind to
WEB_HOST = '127.0.0.1'
WEB_PORT = 8081

# Password salt.  NOTE: If you lose this, all passwords will be lost!
SALT = ''

# Should notification E-mails be sent out?
EMAIL_NOTIFY = True
EMAIL_SENDER = 'pyqual@example.com'
EMAIL_SENDING_HOST = 'mail.example.com'  # Used for HELO command.  If None, will try to get hostname.  Set if you have problems having e-mail rejected.

# Modules that you don't mind being imported by tests
# Be careful what you allow here, enabling modules like sys or os will 
# give test writers access to the whole operating system
IMPORT_WHITELIST = [
    're',
    'datetime',
]

### !!!
# Do not alter the below settings unless you know what you're doing!
### !!!
APP_ROOT = os.path.dirname(os.path.realpath(__file__))

# Config for CherryPy
if not nocherry:
    CP_CONFIG = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(APP_ROOT, 'static'),
        },
    }
