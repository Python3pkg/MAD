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


class Definition:
    """
    Abstract definition that bins an name to an expression to be evaluated
    """

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def accept(self, evaluation):
        raise NotImplementedError("Definition::accept is abstract!")


class DefineService(Definition):
    """
    Definition of a service and the operations it exposes
    """

    def __init__(self, name, body):
        super().__init__(name, body)

    def accept(self, evaluation):
        return evaluation.of_service_definition(self)

    def __repr__(self):
        return "Service(%s, %s)" % (self.name, self.body)


class DefineOperation(Definition):
    """
    Define an operation exposed by a service.
    """

    def __init__(self, name, body):
        super().__init__(name, body)
        self.parameters = []

    def accept(self, evaluation):
        return evaluation.of_operation_definition(self)

    def __repr__(self):
        return "Operation(%s, %s)" % (self.name, str(self.body))


class DefineClientStub(Definition):
    """
    Define a client stub, that is an entity that emits requests at a given frequency
    """

    def __init__(self, name, period, body):
        super().__init__(name, body)
        self.period = period

    def __repr__(self):
        return "DefineClientStub(%d, %s)" % (self.period, self.body)

    def accept(self, evaluation):
        return evaluation.of_client_stub_definition(self)


class Action:
    """
    Abstract all action that can be performed within an operation
    """

    def accept(self, evaluation):
        raise NotImplementedError("Action::accept(evaluation) is abstract!")


class Invocation:
    """
    Abstract invocation of a remote operation
    """

    def __init__(self, service, operation):
        self.service = service
        self.operation = operation

    def accept(self, evaluation):
        raise NotImplementedError("Invocation::accept(evaluation) is abstract!")


class Trigger(Invocation):
    """
    An non-blocking invocation of a remote operation
    """

    def __init__(self, service, operation):
        super().__init__(service, operation)

    def accept(self, evaluation):
        return evaluation.of_trigger(self)

    def __repr__(self):
        return "Trigger(%s, %s)" % (self.service, self.operation)


class Query(Invocation):
    """
    A blocking invocation of a remote operation
    """

    def __init__(self, service, operation):
        super().__init__(service, operation)

    def accept(self, evaluation):
        return evaluation.of_query(self)

    def __repr__(self):
        return "Query(%s, %s)" % (self.service, self.operation)


class Think:
    """
    Simulate a local time-consuming computation
    """

    def __init__(self, duration):
        self.duration = duration

    def accept(self, evaluation):
        return evaluation.of_think(self)

    def __repr__(self):
        return "Think(%d)" % self.duration


class Retry:
    """
    Retry an action a given number of time
    """

    def __init__(self, expression, limit):
        self.expression = expression
        self.limit = limit

    def accept(self, evaluation):
        return evaluation.of_retry(self)

    def __repr__(self):
        return "Retry(%s, %d)" % (str(self.expression), self.limit)


class IgnoreError:
    """
    Ignore error occuring during the evaluation of the given expression
    """

    def __init__(self, expression):
        self.expression = expression

    def accept(self, evaluation):
        return evaluation.of_ignore_error(self)

    def __repr__(self):
        return "IgnoreError(%s)" % str(self.expression)


class Sequence:
    """
    A sequence of actions (i.e., invocation or think)
    """

    def __init__(self, *args, **kwargs):
        self.body = args

    @property
    def first_expression(self):
        return self.body[0]

    @property
    def rest(self):
        if len(self.body) > 2:
            return Sequence(self.body[1:])
        else:
            return self.body[1]

    def accept(self, evaluation):
        return evaluation.of_sequence(self)

    def __repr__(self):
        body = [str(each_expression) for each_expression in self.body]
        return "Sequence(%s)" % ", ".join(body)