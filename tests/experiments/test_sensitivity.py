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


from unittest import TestCase

from mock import MagicMock, PropertyMock, patch

from mad.client import Client, Request
from mad.server import Server
from mad.experiments.sensitivity import ServiceStub, ClientStub
from mad.experiments.sensitivity import SensitivityAnalysis, Parameter


class TestSensitivityAnalysis(TestCase):

    def test_run(self):
        analysis = SensitivityAnalysis()
        analysis.parameters = [
            Parameter("x", "%d", 0, 10, 1),
            Parameter("y", "%d", 0, 20, 1),
            Parameter("z", "%d", 0, 10, 2)
        ]
        analysis.run_count = 100

        with patch.object(SensitivityAnalysis, "one_run") as mock:
            analysis.run()

        self.assertEqual((11 + 21 + 6) * 100, mock.call_count)


class TestParameter(TestCase):

    def test_domain(self):
        parameter = Parameter("x", "%d", 0, 10, 1)
        self.assertEqual(11, len(list(parameter.domain)))

    def test_scaling(self):
        parameter = Parameter("x", "%d", 0, 100, 20, scaling = lambda x: x / 100)

        self.assertEqual([0, 0.2, 0.4, 0.6, 0.8, 1.0], list(parameter.domain))


class TestServiceStub(TestCase):

    def test_response_time(self):
        server = ServiceStub(response_time=20, rejection_rate=0)
        server.on_start()

        def get_time():
            return server.current_time

        client = MagicMock(Client)
        type(client).current_time = PropertyMock(side_effect = get_time)

        request = Request(client)
        request.send_to(server)

        server.run_until(50)

        self.assertTrue(request.is_replied)
        self.assertEqual(20, request._completion_time)


class TestClientStub(TestCase):

    def test_emission_rate(self):
        server = MagicMock(Server)

        client = ClientStub(emission_rate=0.5)
        client.server = server

        client.run_until(100)

        self.assertEqual(50, server.process.call_count)