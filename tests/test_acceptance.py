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


from io import StringIO

from mad.ui import Arguments, Messages, Controller


from unittest import TestCase
from mock import MagicMock

from tests.fakes import InMemoryFileSystem


class AcceptanceTests(TestCase):

    IDENTIFIER = "1"
    MODEL_NAME = "test"

    def setUp(self):
        Arguments._identifier = MagicMock(return_value=self.IDENTIFIER)
        self.display = StringIO()
        self.file_system = InMemoryFileSystem()

    def test_client_server(self):
        self.file_system.define("test.mad", "service DB:"
                                            "   operation Select:"
                                            "      think 5"
                                            "client Browser:"
                                            "   every 5:"
                                            "      query DB/Select")

        self._execute()

        self._verify_opening(self.display)
        self._verify_valid_model(self.display)
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_erroneous_inputs(self):
        self.file_system.define("test.mad", "service DB:"
                                            "   operation Select:"
                                            "      think 5"
                                            "client Browser:"
                                            "   every 5:"
                                            "      query DB/Insert")

        self._execute()

        self._verify_opening(self.display)
        self._verify_invalid_model(self.display)
        self._verify_unknown_operation(self.display)

    def _execute(self):
        mad = Controller(self.display, self.file_system)
        mad.execute(self.MODEL_NAME + ".mad", 1000)

    def _verify_opening(self, display):
        self._verify_version(display)
        self._verify_copyright(display)
        self._verify_disclaimer(display)

    def _verify_disclaimer(self, display):
        self._verify_output(display, Messages.DISCLAIMER)

    def _verify_version(self, display):
        from mad import __version__ as MAD_VERSION
        self._verify_output(display, Messages.VERSION, version=MAD_VERSION)

    def _verify_copyright(self, display):
        from mad import __copyright_years__ as YEARS
        from mad import __copyright_owner__ as OWNER
        self._verify_output(display, Messages.COPYRIGHT, years=YEARS, owner=OWNER)

    def _verify_valid_model(self, display):
        self._verify_output_excludes(display, Messages.INVALID_MODEL)

    def _verify_invalid_model(self, display):
        self._verify_output(display, Messages.INVALID_MODEL)

    def _verify_unknown_operation(self, display):
        self._verify_output(display, Messages.ERROR_UNKNOWN_OPERATION, severity=Messages.SEVERITY_ERROR, service="DB", operation="Insert")

    def _verify_output(self, display, message, **values):
        from re import search, escape
        text = escape(message.format(**values))
        match = search(text, display.getvalue())
        self.assertIsNotNone(match, "\nCould not found text '%s' in output:\n%s" % (str(text), display.getvalue()))

    def _verify_output_excludes(self, display, message, **values):
        from re import search, escape
        text = escape(message.format(**values))
        match = search(text, display.getvalue())
        self.assertIsNone(match, "\nFound unexpected text '%s' in output:\n%s" % (str(text), display.getvalue()))

    def _verify_reports_for(self, entities):
        for each_entity in entities:
            self._verify_report(each_entity)

    def _verify_report(self, entity):
        directory = Arguments.OUTPUT_DIRECTORY.format(name=self.MODEL_NAME, identifier=self.IDENTIFIER)
        report = Arguments.REPORT.format(entity=entity, directory=directory)
        self.assertTrue(self.file_system.has_file(report),
                        "Missing report for '%s' (file '%s').\n Existing files are %s" % (entity, report, str(self.file_system.opened_files.keys())))

    def _verify_log(self):
        directory = Arguments.OUTPUT_DIRECTORY.format(name=self.MODEL_NAME, identifier=self.IDENTIFIER)
        report = Arguments.PATH_TO_LOG_FILE.format(directory=directory, log_file=Arguments.LOG_FILE)
        self.assertTrue(self.file_system.has_file(report),
                        "Missing log file '%s'.\n Existing files are %s" % (report, str(self.file_system.opened_files.keys())))
