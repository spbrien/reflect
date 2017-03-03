import json
# import logging

import falcon

import settings

from lib.models import Connection
from lib.utilities import parse_query_string, get_first_item_if_list

from auth import Authentication
from hooks import hooks

connection = Connection(settings.DB_STRING)


# TODO: Use built-in query string parsing
class ApiResource:
    @falcon.before(hooks.apply_before)
    @falcon.after(hooks.apply_after)
    def on_get(self, req, resp, resource_name=None, resource_id=None):
        """Handles GET requests"""
        # Get all parameters, parsed
        params = parse_query_string(req.query_string)

        # Get each param if exists
        filters = params.get('filters', None)
        fields = params.get('fields', None)
        group_by = get_first_item_if_list(params.get('group_by', None))
        per_page = get_first_item_if_list(params.get('per_page', 25))
        page = get_first_item_if_list(params.get('page', 1))
        order = get_first_item_if_list(params.get('order', 'desc'))
        order_by = get_first_item_if_list(
            params.get('order_by', '%s' % settings.ID_FIELD)
        )

        if resource_name and not resource_id:
            items = connection.query(
                table=resource_name,
                filters=filters,
                fields=fields,
                group_by=group_by if group_by else None,
                per_page=per_page,
                page=page,
                order=order,
                order_by=order_by
            )
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/json'
            resp.body = json.dumps({
                'page': int(page),
                'per_page': int(per_page),
                '_items': items
            })
            return

        if resource_name and resource_id:
            items = connection.query(
                table=resource_name,
                filters=['%s==%s' % (settings.ID_FIELD, resource_id)]
            )
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/json'
            if items:
                resp.body = json.dumps(items[0])
                return
            else:
                raise falcon.HTTPNotFound(
                    title="404",
                    description="Not Found"
                )

        items = connection.get_database_map()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = 'application/json'
        resp.body = json.dumps(items)
        return

    def on_post(self, req, resp, resource_name=None, resource_id=None):
        if resource_name and not resource_id:
            data = json.loads(req.stream.read())
            result = connection.insert(table=resource_name, data=data)
            resp.status = falcon.HTTP_201  # This is the default status
            resp.content_type = 'application/json'
            resp.body = json.dumps(result)
            return
        else:
            raise falcon.HTTPBadRequest(
                title="Error",
                description="Method not allowed for this endpoint"
            )

    def on_put(self, req, resp, resource_name=None, resource_id=None):
        if resource_name and resource_id:
            data = json.loads(req.stream.read())
            result = connection.update(
                table=resource_name,
                id=resource_id,
                data=data
            )
            resp.status = falcon.HTTP_200  # This is the default status
            resp.content_type = 'application/json'
            resp.body = json.dumps(result)
            return
        else:
            raise falcon.HTTPBadRequest(
                title="Error",
                description="Method not allowed for this endpoint"
            )

    def on_delete(self, req, resp, resource_name=None, resource_id=None):
        if resource_name and resource_id:
            result = connection.delete(
                table=resource_name,
                id=resource_id,
            )
            resp.status = falcon.HTTP_200  # This is the default status
            resp.content_type = 'application/json'
            resp.body = json.dumps(result)
            return
        else:
            raise falcon.HTTPBadRequest(
                title="Error",
                description="Method not allowed for this endpoint"
            )


# falcon.API instances are callable WSGI apps
app = falcon.API(
    middleware=[Authentication()]
)

# Resources are represented by long-lived class instances
api = ApiResource()

app.add_route('/{resource_name}', api)
app.add_route('/{resource_name}/{resource_id}', api)
