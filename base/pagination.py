from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param



class LimitPagination(LimitOffsetPagination):
    offset_query_param = 'offset'
    limit_query_param = 'limit'
    max_limit = 100

    def get_last_link(self):
        if self.count == 0:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = (self.count // self.limit) * self.limit

        if offset <= 0:
            return remove_query_param(url, self.offset_query_param)

        return replace_query_param(url, self.offset_query_param, offset)

    def get_first_link(self):
        if self.count == 0:
            return None

        url = self.request.build_absolute_uri()
        return remove_query_param(url, self.offset_query_param)

    def get_paginated_response(self, data):
        return Response({
            'links': OrderedDict([
                ('first', self.get_first_link()),
                ('last', self.get_last_link()),
                ('next', self.get_next_link()),
                ('prev', self.get_previous_link())
            ]),
            
            'results': data,

            'meta': {
                'pagination': OrderedDict([
                    ('count', self.count),
                    ('limit', self.limit),
                    ('offset', self.offset),
                ])
            }
        })