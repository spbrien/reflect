from lib.register_hooks import hooks


# This is a sample hook
# Use hooks to transform data before or after a request,
# or implement logging, etc
@hooks.before_resource('GET', 'wp_posts')
def print_params(req, resp, resource, params):
    print params
