#!/usr/bin/env python
import urllib
import re


def convert_values_to_list(values):
    if ',' in values:
        return values.split(',')
    return [values]


def parse_query_string(query_string):
    q = urllib.unquote(query_string).decode('utf8')
    return {
        item.split('=', 1)[0]: convert_values_to_list(item.split('=', 1)[1])
        for item in q.split('&') if item
    }


def get_first_item_if_list(item):
    if isinstance(item, (list, tuple)) and not isinstance(item, basestring):
        return item[0]
    return item


def get_json_from_req(req):
    pass


def find_error_msg(text):
    matches = re.findall(r'\"(.+?)\"', text)
    # matches is now ['String 1', 'String 2', 'String3']
    if matches:
        return matches[0] if len(matches) == 1 else ", ".join(matches)
    return None
