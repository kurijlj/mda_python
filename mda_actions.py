#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Measurement Data Anlysis - a small GUI app for analisys of measurement data.
#
#  Copyright (C) 2020 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================


# =============================================================================
#
# 2020-09-15 Ljubomir Kurij <kurijlj@gmail.com>
#
# * mda_actions.py: created.
#
# =============================================================================


# ============================================================================
#
# TODO:
#
#
# ============================================================================


# ============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ============================================================================


# =============================================================================
# Modules import section
# =============================================================================

from os.path import isfile  # Test for existance of a file.
import mda_models as mdam
import mda_views as mdav


# =============================================================================
# Global constants
# =============================================================================


# =============================================================================
# Utility classes and functions
# =============================================================================

class ProgramAction(object):
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf

    def execute(self):
        """TODO: Put method docstring HERE.
        """


def formulate_action(Action, **kwargs):
    """Factory method to create and return proper action object.
    """

    return Action(**kwargs)


# =============================================================================
# App action classes
# =============================================================================

class ProgramUsageAction(ProgramAction):
    """Program action that formats and displays usage message to the stdout.
    """

    def __init__(self, parser, exitf):
        super().__init__(exitf)
        self._usage_message = \
            '{usage}Try \'{prog} --help\' for more information.'\
            .format(usage=parser.format_usage(), prog=parser.prog)

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        print(self._usage_message)
        self._exit_app()


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def __init__(self, prog, ver, year, author, license, exitf):
        super().__init__(exitf)
        self._version_message = \
            '{0} {1} Copyright (C) {2} {3}\n{4}'\
            .format(prog, ver, year, author, license)

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        print(self._version_message)
        self._exit_app()


class DefaultAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    def __init__(self, prog, exitf, data_file, delimiter):
        super().__init__(exitf)
        self._program_name = prog
        self._data_file = data_file
        self._delimiter = delimiter

        # Define all models.
        self.data_model = None

        # Initialize views.
        self._mainscreen = mdav.TkiAppMainWindow(controller=self)

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        # Do some basic sanity checks first. Check if user has supplied a
        # data file, ...
        if self._data_file is None:
            print(
                '{0}: Missing data file argument.'
                .format(self._program_name)
                )
            self._exit_app()

        # ... then check if given file exist at all.
        if not isfile(self._data_file):
            print(
                '{0}: File \'{1}\' does not exist or is directory.'
                .format(self._program_name, self._data_file)
                )

            self._exit_app()

        print(
            '{0}: Reading file \'{1}\'.\n\n'
            .format(self._program_name, self._data_file)
            )
        data_reader = mdam.CSVDataReader()
        data = data_reader.read_data(self._data_file, self._delimiter)
        headers = data_reader.headers
        data_reader.print_error_report()
        print('\n')

        if data is not None:
            # Print some info to the command line.
            print('{0}: Starting GUI ...'.format(self._program_name))

            # Initialize all models.
            self.data_model = mdam.Graph(data, headers)

            # We have all neccessary files. Start the GUI.
            self._mainscreen.title(self._program_name)
            self._mainscreen.update()  # Update screen.
            self._mainscreen.mainloop()

            # Print to command line that we are freeing memory and ...
            print(
                '{0}: Freeing allocated memory ...'
                .format(self._program_name))

        # ... closing app.
        print('{0}: Closing the app ...'.format(self._program_name))

        # Do the cleanup and exit application.
        self._exit_app()
