# import requests

from lib.register_auth import AuthMiddleware


class Authentication(AuthMiddleware):
    # Connect to an external Auth server,
    # or implement your own local authentication
    # ------------------------------------------

    # Check username and password against stored/valid values
    # -------------------------------------------------------
    # def _auth_valid(self, username=None, password=None):
    #     pass

    # Retreive account info based on info in the requests
    # -------------------------------------------------------
    # def _get_account_info(self, req):
    #     pass

    pass
