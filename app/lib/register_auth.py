import base64

import falcon

from app import settings


class AuthMiddleware(object):
    # TODO: Implement real auth using local db

    # This function will be overridden by subclass
    # ----------------------------------------------
    def _auth_valid(self, username=None, password=None):
        # Default allowed credentials
        valid_username = settings.ADMIN_USERNAME
        valid_password = settings.ADMIN_PASSWORD

        # Check validity
        if valid_password and valid_username  \
                and username == valid_username \
                and password == valid_password:
            return True

        return False

    # This function will be overridden by subclass
    # ----------------------------------------------
    def _get_account_info(self, req):
        auth_string = req.headers.get('AUTHORIZATION', None)
        if auth_string:
            try:
                encoded = auth_string.split(' ')[1]
                decoded = base64.b64decode(encoded).decode('utf8')
                return decoded.split(':') if ':' in decoded else None
            except:
                raise falcon.HTTPBadRequest()

        raise falcon.HTTPUnauthorized(
            title='Authorization required'
        )

    # This checks user and role against the allowed values
    def process_request(self, req, resp):
        # Set default roles
        role = 'anonymous'

        # parse relevant info from path
        path = req.path[1:]
        resource = path.split('/')[0] if path and '/' in path else path
        method = req.method

        if not resource:
            return

        # Get auth schema and endpoint settings
        schema = settings.AUTHENTICATION_SETTINGS.get(method, None)
        endpoint_settings = schema.get(resource, None) if resource else None

        if endpoint_settings \
                and 'anonymous' in endpoint_settings['allowed_roles']:
            return

        # Get Username and Password, or Token from Auth String
        (username, password) = self._get_account_info(req)

        # If we're allowed, return
        if endpoint_settings:
            if username in endpoint_settings['allowed_users']:
                return
            if role in endpoint_settings['allowed_roles']:
                return


        # Else if we have the right credentials
        if self._auth_valid(username, password):
            return

        # Else, return auth error
        raise falcon.HTTPUnauthorized(
            title='Authorization required',
        )
