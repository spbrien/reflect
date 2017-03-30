#!/usr/bin/env python


class Hooks():
    before = []
    after = []

    def before_resource(self, method, resource_name):
        def decorate(f):
            def hook_function(req, resp, resource, params):
                if resource_name == params['resource_name'] \
                        and req.method == method:
                    f(req, resp, resource, params)
                else:
                    pass
            self.before.append(hook_function)
        return decorate

    def before_item(self, method, resource_name):
        def decorate(f):
            def hook_function(req, resp, resource, params):
                if resource_name == params['resource_name'] \
                        and req.method == method \
                        and params['resource_id']:
                    f(req, resp, resource, params)
                else:
                    pass
            self.before.append(hook_function)
        return decorate

    def after_resource(self, method, resource_name):
        def decorate(f):
            def hook_function(req, resp, resource):
                path = req.path[1:]
                res_name = path.split('/')[0] if path and '/' in path else path
                if resource_name == res_name \
                        and req.method == method:
                    f(req, resp, resource)
                else:
                    pass
            self.after.append(hook_function)
        return decorate

    def after_item(self, method, resource_name):
        def decorate(f):
            def hook_function(req, resp, resource):
                path = req.path[1:]
                res_name = path.split('/')[0] if path and '/' in path else path
                res_id = path.split('/')[1] if path and '/' in path else None
                if resource_name == res_name \
                        and req.method == method \
                        and res_id:
                    f(req, resp, resource)
                else:
                    pass
            self.after.append(hook_function)
        return decorate

    def apply_before(self, req, resp, resource, params):
        for f in self.before:
            f(req, resp, resource, params)

    def apply_after(self, req, resp, resource):
        for f in self.after:
            f(req, resp, resource)


hooks = Hooks()
