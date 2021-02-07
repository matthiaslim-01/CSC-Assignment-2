import json
from http import HTTPStatus
from http.cookies import SimpleCookie
from logging import log
from lib.debugtest import debug_test
from lib.constants import ALLOWED_ORIGINS
from lib.webexception import WebException
from lib.controllers.auth_controller import login, register
from lib.controllers.payments_controller import (
    create_checkout_session,
    customer_portal,
    get_checkout_session,
    get_publishable_key,
    webhook_received,
)
from lib.services.dynamodb_service import get_session_username, get_subscription_plan
# from lib.controllers.commentManagement_controller import get_comments


APILIST = {
    "GET": {
        "test": debug_test,
        "get-publishable-key": get_publishable_key,
        "get-checkout-session": get_checkout_session,
        # "get-comments": get_comments,
    },
    "POST": {
        "login": login,
        "register": register,
        "create-checkout-session": create_checkout_session,
        "customer-portal": customer_portal,
        "webhook": webhook_received,
    },
}


class Request:
    def __init__(self, event):
        self.event = event
        self.method = event.get("httpMethod", "")
        path = event.get("path", "")
        self.endpoint = (
            path.split("/")[-1] if not path.endswith("/") else path.split("/")[-2]
        )
        self.headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        self.origin = self.headers.get("origin")
        raw_cookie = self.headers.get("cookie", "")
        self.cookies = SimpleCookie(raw_cookie if raw_cookie is not None else "")

        self.function = None
        self.data = {}

        self.username = None
        self.session_token = None
        self.paiduser = False

    def resolve_function(self):
        self.function = APILIST.get(self.method, {}).get(self.endpoint, None)
        if not self.function:
            raise WebException(status_code=HTTPStatus.NOT_FOUND, message="Invalid API")

        return self

    def check_csrf(self):
        # if self.method in ["POST", "PUT", "DELETE"]:
        #     csrf_header = self.headers.get("x-csrf-token")
        #     csrf_morsel = self.cookies.get("csrf-cookie")
        #     if not csrf_morsel or not csrf_header or csrf_morsel.value != csrf_header:
        #         raise WebException(
        #            status_code=HTTPStatus.BAD_REQUEST, message="Invalid CSRF"
        #         )

        return self

    def retrieve_user(self):
        session_cookie = self.cookies.get("session", None)
        if session_cookie is None:
            self.session_token = None
        else:
            self.session_token = session_cookie.value

        if self.endpoint not in ["login", "test", "get-publishable-key", "webhook", "create-checkout-session"]:
            self.username = get_session_username(self.session_token)
            if not self.username:
                raise WebException(
                    status_code=HTTPStatus.UNAUTHORIZED, message="Unauthenticated User"
                )
            self.paiduser = get_subscription_plan(self.username)

        return self

    def parse_data(self):
        if self.method in ["GET", "DELETE"]:
            qsp = self.event.get("queryStringParameters", {})
            self.data = {} if qsp is None else qsp
        elif self.method in ["POST", "PUT"]:
            body = self.event.get("body", "{}")
            body = "{}" if not body else body
            try:
                self.data = json.loads(body)
            except Exception as ex:
                raise WebException(
                    status_code=HTTPStatus.BAD_REQUEST, message="Invalid JSON"
                ) from ex
        return self


class Response:
    def __init__(self, origin):
        self.body = {}
        self.cookies = []

        self.status_code = HTTPStatus.OK
        self.message = "Success"

    def set_session(self, token):
        self.cookies.append(f"session={token}; Path=/;")
        return self

    def clear_session(self):
        self.cookies = ["session=; Max-Age=0; Path=/;"]
        return self
