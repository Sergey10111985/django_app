import time

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest


def set_useragent_on_request_middleware(get_response):
    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META.get('HTTP_USER_AGENT')
        response = get_response(request)
        print("after get response")
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print('requests_count', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses_count', self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print('got', self.exceptions_count, 'exceptions so far')


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_ips = {}

    def __call__(self, request: HttpRequest):
        t = time.time()
        ip = request.META.get('REMOTE_ADDR')
        if ip not in self.user_ips.keys():
            self.user_ips.update({ip: t})
            print('NOT')
        else:
            if t - self.user_ips[ip] < 3:
                self.user_ips.update({ip: t})
                raise PermissionDenied
            else:
                self.user_ips.update({ip: t})

        response = self.get_response(request)
        return response
