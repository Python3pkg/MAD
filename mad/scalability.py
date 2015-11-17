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


class Control(Action):

    def __init__(self, subject):
        super().__init__()
        self._subject = subject

    def fire(self):
        self._subject.control()

    def __str__(self):
        return "Adjust unit count"


class Controller(Agent):
    """
    Abstract controller adjusting the number of active processing unit in a cluster
    """

    def __init__(self, control_rate=0.1):
        super().__init__("scalability controller")
        self._control_rate = control_rate
        self._cluster = None

    @property
    def cluster(self):
        return self._cluster

    @cluster.setter
    def cluster(self, cluster):
        self._cluster = cluster

    @property
    def control_rate(self):
        return self._control_rate

    @property
    def control_period(self):
        return int(1 / self.control_rate)

    def on_start(self):
        self.schedule_next_control()

    def schedule_next_control(self):
        self.schedule_in(Control(self), self.control_period)

    def control(self):
        new_signal = self.signal
        self.cluster.active_unit_count = new_signal
        self.schedule_next_control()

    @property
    def signal(self):
        return self.cluster.active_unit_count


class FixedCluster(Controller):
    """
    A "does-nothing" control strategy. Returns the current number of units in the cluster
    """

    def __init__(self):
        super().__init__(0.1)


class UtilisationController(Controller):
    """
    Control the number of active processing units
    """

    def __init__(self, min, max, step):
        super().__init__(0.1)
        self._min = min
        self._max = max
        self._step = step

    @Controller.signal.getter
    def signal(self):
        if self.is_too_low():
            return round(self.remove_units())
        elif self.is_too_high():
            return round(self.add_units())
        else:
            return self.cluster.active_unit_count

    def is_too_high(self):
        return self.cluster.utilisation > self._max

    def is_too_low(self):
        return self.cluster.utilisation < self._min

    def add_units(self):
        return self.cluster.active_unit_count + self._step

    def remove_units(self):
        return self.cluster.active_unit_count - self._step

    def __str__(self):
        return "[%d, %d] %d -> %d" % (self._min, self._max, self.cluster.active_unit_count, self._step)
