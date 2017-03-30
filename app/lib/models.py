import operator
from contextlib import contextmanager

import falcon

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app import settings
from app.lib.utilities import find_error_msg

# TODO: Process relationships and complex join queries
# TODO: Group By queries
# TODO: Limit fields


# function to get the column name
def column_name(column):
    return str(column).split('.')[1]


# function to get the column contents
def column_contents(table, column):
    return str(getattr(table, column_name(column)))


# function to collect query results
def collect_results(table_class, query):
    return [
        {
             column_name(col): column_contents(item, col)
             for col in table_class.__table__.columns
        }
        for item in query
    ]


def parse_filters(filters):
    return [
        get_operator(f) for f in filters
    ]


def get_operator(string):
    operator_map = {
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '<=': operator.le,
        '>': operator.gt,
        '<': operator.lt,
    }
    for op in operator_map:
        if op in string:
            plan = {
                'operator': operator_map[op],  # Will be function
                'property_name': string.split(op)[0],
                'property_value': string.split(op)[1]
            }

            def create_filter_function(query_base, queried_class):
                return getattr(query_base, 'filter')(
                    plan['operator'](
                        getattr(
                            queried_class,
                            plan['property_name']
                        ),
                        plan['property_value']
                    )
                )
            return create_filter_function


class Connection():

    def __init__(self, db_string):
        self.base = automap_base()
        self.engine = create_engine(db_string)
        self.base.prepare(self.engine, reflect=True)

        @contextmanager
        def session_scope():
            """Provide a transactional scope around a series of operations."""
            session = Session(self.engine)
            try:
                yield session
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        self.session = session_scope

    def get_database_map(self):
        tables = {
            table_class.__name__: [
                column_class.name for column_class
                in table_class.__table__.columns
            ] for table_class in self.base.classes
        }
        return tables

    def get_table_contents(
        self,
        table_class,
        filters=None,
        fields=None,
        group_by=None,
        per_page=25,
        page=1,
        order="desc",
        order_by="%s" % settings.ID_FIELD
    ):

        def construct_query_with_filters(filter_function):
            def apply_filter(query_base):
                return filter_function(query_base, table_class)
            return apply_filter

        # if we don't have any filters, return all results
        if table_class and not filters:
            with self.session() as session:
                q = session.query(table_class) \
                    .order_by("%s %s" % (order_by, order)) \
                    .offset((int(page)-1)*int(per_page)) \
                    .limit(int(per_page)) \
                    .all()
                return collect_results(table_class, q)

        # if we have filters, apply them
        if table_class and filters:
            with self.session() as session:
                query_base = session.query(table_class)
                full = reduce(
                    lambda x, y: construct_query_with_filters(y)(x),
                    filters,
                    query_base
                )
                return collect_results(
                    table_class,
                    full.order_by("ID desc")
                        .offset((int(page)-1)*int(per_page))
                        .limit(int(per_page))
                        .all()
                )

        return None

    def query(
        self,
        table=None,
        filters=None,
        fields=None,
        group_by=None,
        per_page=25,
        page=1,
        order="desc",
        order_by="%s" % settings.ID_FIELD
    ):
        # get query filters
        query_filters = parse_filters(filters) if filters else None

        # Try to find the requested table, return None if non-existant fs
        table_to_query_class = next(
            (
                table_class for table_class
                in self.base.classes
                if table_class.__name__.lower() == table.lower()
            ),
            None
        )

        if table_to_query_class:
            return self.get_table_contents(
                table_to_query_class,
                filters=query_filters,
                fields=fields,
                group_by=group_by,
                per_page=per_page,
                page=page,
                order=order,
                order_by=order_by
            )
        else:
            raise falcon.HTTPNotFound(
                title="404",
                description="Not found"
            )

    def insert(self, table=None, data=None):
        Table = next(
            (
                table_class for table_class
                in self.base.classes
                if table_class.__name__.lower() == table.lower()
            ),
            None
        )
        columns = [
            column_class.name for column_class
            in Table.__table__.columns
        ]
        to_insert = {
            key: value for key, value in data.iteritems()
            if key in columns
        }
        if Table:
            item = Table(**to_insert)
            with self.session() as session:
                try:
                    session.add(item)
                    session.commit()
                    return self.get_table_contents(
                        Table,
                        per_page=1
                    )[0]
                except Exception as e:
                    print e
                    msg = find_error_msg(e.message)
                    raise falcon.HTTPBadRequest(
                        title="Error",
                        description=msg
                    )
        else:
            raise falcon.HTTPNotFound(
                title="404",
                description="Not found"
            )

    def update(self, table=None, id=None, data=None):
        Table = next(
            (
                table_class for table_class
                in self.base.classes
                if table_class.__name__.lower() == table.lower()
            ),
            None
        )
        if Table:
            with self.session() as session:
                try:
                    q = session.query(Table)
                    q = q.filter(getattr(Table, settings.ID_FIELD) == id)
                    record = q.one()
                    if record:
                        for key, value in data.iteritems():
                            if hasattr(record, key):
                                setattr(record, key, value)
                        session.commit()
                        return {
                             column_name(col): column_contents(record, col)
                             for col in Table.__table__.columns
                        }
                    else:
                        raise falcon.HTTPNotFound(
                            title="404",
                            description="Not found"
                        )

                except Exception as e:
                    print e
                    msg = find_error_msg(e.message)
                    raise falcon.HTTPBadRequest(
                        title="Error",
                        description=msg
                    )
        else:
            raise falcon.HTTPNotFound(
                title="404",
                description="Not found"
            )

    def delete(self, table=None, id=None):
        Table = next(
            (
                table_class for table_class
                in self.base.classes
                if table_class.__name__.lower() == table.lower()
            ),
            None
        )
        if Table:
            with self.session() as session:
                try:
                    q = session.query(Table)
                    q = q.filter(getattr(Table, settings.ID_FIELD) == id)
                    record = q.one()
                    if record:
                        session.delete(record)
                    else:
                        raise falcon.HTTPNotFound(
                            title="404",
                            description="Not found"
                        )

                except Exception as e:
                    print e
                    msg = find_error_msg(e.message)
                    raise falcon.HTTPBadRequest(
                        title="Error",
                        description=msg
                    )

        else:
            raise falcon.HTTPNotFound(
                title="404",
                description="Not found"
            )
