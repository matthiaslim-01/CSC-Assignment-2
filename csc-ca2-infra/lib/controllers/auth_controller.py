from http import HTTPStatus
from botocore.utils import _parse_timestamp_with_tzinfo
from lib.services.dynamodb_service import store_session, remove_session
from uuid import uuid4
from lib.webexception import WebException

def login(request,response):
    #Take username and password to authenticate, then when user is authenticated generate session and store session. 
    data = request.data
    username = data["username"]
    password = data["password"]
    
    #set authenticate function here. 
    authenticated = True #proxy for now

    if authenticated:
        sessionToken = str(uuid4())
        store_session(sessionToken, username)
        response.set_session(sessionToken)
    else:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="Invalid credentials") 

    return response

def register(request,response):
    #DO STUFF
    data = request.data
    full_name = data["full_name"]
    username = data["username"]
    password = data["password"]
    
    
    #set authenticate function here. 
    authenticated = True #proxy for now

    if authenticated:
        sessionToken = str(uuid4())
        store_session(sessionToken, username)
        response.set_session(sessionToken)
    else:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="Invalid credentials") 

    return response
   

def logout(request, response):
    remove_session(request.session_token)
    response.clear_session()
    return response