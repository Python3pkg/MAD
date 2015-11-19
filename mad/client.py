#!/usr/bin/env python

#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#


from mad.simulation import Agent, Action
from mad.math import LowerBound


class Request:
    """
    A request send by a 'client' to a 'server'
    """

    def __init__(self, sender):
        self._sender = sender
        self._emission_time = None
        self._completion_time = None

    def send_to(self, server):
        self._emission_time = self._sender.current_time
        server.process(self)

    @property
    def response_time(self):
        assert self.is_replied, "Response is not available before completion"
        return self._completion_time - self._emission_time

    @property
    def is_replied(self):
        return self._completion_time is not None

    def reply(self):
        self._completion_time = self._sender.current_time
        self._sender.on_completion_of(self)

    def reject(self):
        self._sender.on_rejection_of(self)


class Send(Action):
    """
    Capture the client sending a single request, and then scheduling the departure of the next request
    """

    def __init__(self, sender):
        self._sender = sender

    def fire(self):
        self._sender.send_request()

    def __str__(self):
        return "Sending request"


class Client(Agent):
    """
    A 'client' emits requests at a fixed interval
    """

    def __init__(self, identifier, inter_request_period):
        super().__init__(identifier)
        self._inter_request_period = LowerBound(inter_request_period, 1)
        self._server = None
        self._meter = Meter()

    @property
    def inter_request_period(self):
        return int(self._inter_request_period.value_at(self.current_time))

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, new_server):
        self._server = new_server

    def on_start(self):
        self.prepare_next_request()

    def record_state(self):
        self.record([
            ("rejection", "%d", self._meter.rejection_count)
        ])
        self._meter.reset()

    def send_request(self):
        Request(self).send_to(self._server)

    def prepare_next_request(self):
        self.schedule_in(Send(self), delay=self.inter_request_period)

    def on_completion_of(self, request):
        self.prepare_next_request()

    def on_rejection_of(self, request):
        self._meter.new_rejection()
        self.prepare_next_request()


class ClientStub(Client):
    """
    A client stub that send request at a fixed rate, regardless of whether they are rejected or successful
    """

    def __init__(self, name="client stub", inter_request_period=10):
        super().__init__(name, inter_request_period)

    def send_request(self):
        Request(self).send_to(self.server)
        self.prepare_next_request()

    def on_completion_of(self, request):
        pass

    def on_rejection_of(self, request):
        pass


class Meter:
    """
    Compute some statistics about rejections
    """

    NO_RESPONSE_TIME = -1

    def __init__(self):
        self._request_count = 0
        self._total_response_time = 0
        self._success_count = 0
        self._rejection_count = 0

    def new_request(self):
        self._request_count += 1

    @property
    def throughput(self):
        return self._success_count

    @property
    def request_count(self):
        return self._request_count

    def new_success(self, request):
        self._success_count += 1
        self._total_response_time += request.response_time

    @property
    def average_response_time(self):
        if self._success_count > 0:
            return self._total_response_time / self._success_count
        else:
            return Meter.NO_RESPONSE_TIME

    def new_rejection(self):
        self._rejection_count += 1

    @property
    def rejection_count(self):
        return self._rejection_count

    def reset(self):
        self.__init__()
