#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import memcache


class User(ndb.Model):
    """Sub model for representing an author."""
    userid = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    access_token = ndb.StringProperty(indexed=False)


class Greeting(messages.Message):
    """Greeting that stores a message."""
    message = messages.StringField(1)


class Message(messages.Message):
    """Greeting that stores a message."""
    message = messages.StringField(1)


class GreetingCollection(messages.Message):
    """Collection of Greetings."""
    items = messages.MessageField(Greeting, 1, repeated=True)


STORED_GREETINGS = GreetingCollection(items=[
    Greeting(message='hello world!'),
    Greeting(message='goodbye world!'),
])


class Location(messages.Message):
    x = messages.FloatField(1, required=True)
    y = messages.FloatField(2, required=True)


@endpoints.api(name='api', version='v1')
class Api(remote.Service):

    @endpoints.method(
        # This method does not take a request message.
        message_types.VoidMessage,
        # This method returns a GreetingCollection message.
        Greeting,
        path='api',
        http_method='GET',
        name='greetings.list')
    def list_greetings(self, unused_request):
        return Greeting(message='Welcome to Techcrunch runners API!')

    # ResourceContainers are used to encapsuate a request body and url
    # parameters. This one is used to represent the Greeting ID for the
    # greeting_get method.
    GET_RESOURCE = endpoints.ResourceContainer(
        # The request body should be empty.
        message_types.VoidMessage,
        # Accept one url parameter: and integer named 'id'
        id=messages.IntegerField(1, variant=messages.Variant.INT32))

    CALLBACK_RESOURCE = endpoints.ResourceContainer(
        message_types.VoidMessage,
        code=messages.StringField(1, variant=messages.Variant.STRING, required=True)
    )

    @endpoints.method(
        CALLBACK_RESOURCE,
        Message,
        path='callback',
        http_method='POST')
    def callback(self, request):
        # memcache.add(key='code', value=request.code, time=3600)
        return Message(message=request.code)

    @endpoints.method(
        message_types.VoidMessage,
        Message,
        path='auth/access_token',
        http_method='GET')
    def access(self, request):
        data = {
            "client_id": 'cf0a3f5a8d404bb8a15122c37cce5f74',
            'redirect_uri': 'https://techcrunchrunners.appspot.com/_ah/api/api/v1/api',
            'response_type': 'code',
            'code':  memcache.get(key='code')
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url='https://api.instagram.com/oauth/access_token',
            payload=str(data),
            method=urlfetch.POST,
            headers=headers)
        user = User(
            access_token=result.access_token,
            name=result.user.username,
            userid=result.user.userid,
            email=result.user.email
        )
        return Message(message='success!')

api = endpoints.api_server([Api])