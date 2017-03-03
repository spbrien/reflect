# Using Scotchbox with a wordpress database for testing
# Get one here --> https://box.scotch.io/
# Even though (and maybe because) wordpress databases suck
# ----------------------------------
DB_STRING = 'mysql+mysqldb://root:root@192.168.33.133:3306/scotchbox'


# Auth Server
# ----------------------------------
AUTHENTICATION_SERVER = ''
AUTHENTICATION_SCOPE = ''


# Default User -- THIS OPTION SHOULD ONLY BE SET FOR DEVELOPMENT
# Authentication class should be subclassed and set up
# to use an outside Auth server
# ----------------------------------
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'test'
# ADMIN_USERNAME = None
# ADMIN_PASSWORD = None


# Expose endpoints (tables) by Role for each HTTP verb
# TODO: Add column restriction functionality as well
# ----------------------------------
AUTHENTICATION_SETTINGS = {
    'GET': {
        'wp_posts': {
            'allowed_users': [],
            'allowed_roles': []
        }
    },
    'POST': {},
    'PUT': {},
    'PATCH': {},
    'DELETE': {}
}


# Field to match when fetching single items
# ----------------------------------
ID_FIELD = 'ID'
