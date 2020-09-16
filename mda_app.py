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
# 2020-09-16 Ljubomir Kurij <kurijlj@gmail.com>
#
# * mda_app.py: created.
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

import argparse
import mda_actions as mdak


# =============================================================================
# Global constants
# =============================================================================


# =============================================================================
# Utility classes and functions
# =============================================================================

def _format_epilogue(epilogue_addition, bug_mail):
    """Formatter for generating help epilogue text. Help epilogue text is an
    additional description of the program that is displayed after the
    description of the arguments. Usually it consists only of line informing
    to which email address to report bugs to, or it can be completely
    omitted.

    Depending on provided parameters function will properly format epilogue
    text and return string containing formatted text. If none of the
    parameters are supplied the function will return None which is default
    value for epilogue parameter when constructing parser object.
    program.add_argument(
            '-d', '--delimiter',
            action='store',
            metavar='DELIMITER',
            type=str,
            help='field delimiter. Default value is \",\"',
            group='general options'
        )
    program.add_argument(
            'data_file',
            metavar='DATA_FILE',
            type=str,
            nargs='?',
            help='a CSV file containing graph data'
        )
    """

    fmt_mail = None
    fmt_epilogue = None

    if epilogue_addition is None and bug_mail is None:
        return None

    if bug_mail is not None:
        fmt_mail = 'Report bugs to <{bug_mail}>.'\
            .format(bug_mail=bug_mail)
    else:
        fmt_mail = None

    if epilogue_addition is None:
        fmt_epilogue = fmt_mail

    elif fmt_mail is None:
        fmt_epilogue = epilogue_addition

    else:
        fmt_epilogue = '{addition}\n\n{mail}'\
            .format(addition=epilogue_addition, mail=fmt_mail)

    return fmt_epilogue


# =============================================================================
# Command line app class
# =============================================================================

class CommandLineApp(object):
    """Actual command line app object containing all relevant application
    information (NAME, VERSION, DESCRIPTION, ...) and which instantiates
    action that will be executed depending on the user input from
    command line.
    """

    def __init__(
            self,
            program_name=None,
            program_description=None,
            program_license=None,
            version_string=None,
            year_string=None,
            author_name=None,
            author_mail=None,
            epilogue=None):

        self.program_license = program_license
        self.version_string = version_string
        self.year_string = year_string
        self.author_name = author_name
        self.author_mail = author_mail

        fmt_epilogue = _format_epilogue(epilogue, author_mail)

        self._parser = argparse.ArgumentParser(
                prog=program_name,
                description=program_description,
                epilog=fmt_epilogue,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )

        # Since we add argument options to groups by calling group
        # method add_argument, we have to sore all that group objects
        # somewhere before adding arguments. Since we want to store all
        # application relevant data in our application object we use
        # this list for that purpose.
        self._argument_groups = []

        self._action = None

    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute
        neat and hides implementation details.
        """
        return self._parser.prog

    @property
    def program_description(self):
        """Utility function that makes accessing program description
        attribute neat and hides implementation details.
        """
        return self._parser.description

    def add_argument_group(self, title=None, description=None):
        """Adds an argument group to application object.
        At least group title must be provided or method will rise
        NameError exception. This is to prevent creation of titleless
        and descriptionless argument groups. Although this is allowed bu
        argparse module I don't see any use of a such utility."""

        if title is None:
            raise NameError('Missing arguments group title.')

        group = self._parser.add_argument_group(title, description)
        self._argument_groups.append(group)

        return group

    def _group_by_title(self, title):
        group = None

        for item in self._argument_groups:
            if title == item.title:
                group = item
                break

        return group

    def add_argument(self, *args, **kwargs):
        """Wrapper for add_argument methods of argparse module. If
        parameter group is supplied with valid group name, argument will
        be added to that group. If group parameter is omitted argument
        will be added to parser object. In a case of invalid group name
        it rises ValueError exception.
        """

        if 'group' not in kwargs or kwargs['group'] is None:
            self._parser.add_argument(*args, **kwargs)

        else:
            group = self._group_by_title(kwargs['group'])

            if group is None:
                raise ValueError(
                        'Trying to reference nonexisten argument group.'
                    )

            kwargsr = {k: kwargs[k] for k in kwargs if k != 'group'}
            group.add_argument(*args, **kwargsr)

    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of a parser object. It also
        instantiates action object that will be executed based on a
        input from command line.
        """

        arguments = self._parser.parse_args(args, namespace)

        if arguments.usage:
            self._action = mdak.formulate_action(
                mdak.ProgramUsageAction,
                parser=self._parser,
                exitf=self._parser.exit)

        elif arguments.version:
            self._action = mdak.formulate_action(
                mdak.ShowVersionAction,
                prog=self._parser.prog,
                ver=self.version_string,
                year=self.year_string,
                author=self.author_name,
                license=self.program_license,
                exitf=self._parser.exit)

        else:
            delimiter = ','

            if arguments.delimiter:
                delimiter = arguments.delimiter

            self._action = mdak.formulate_action(
                mdak.DefaultAction,
                prog=self._parser.prog,
                exitf=self._parser.exit,
                data_file=arguments.data_file,
                delimiter=delimiter)

    def run(self):
        """This method executes action code.
        """

        self._action.execute()


# =============================================================================
# Script main body
# =============================================================================

if __name__ == '__main__':

    PROGRAM_DESCRIPTION = '\
Small GUI app to inspect and analyse 2D measurement data.\n\
Mandatory arguments to long options are mandatory for short options too.'
    PROGRAM_LICENSE = '\
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\
\n\
This is free software: you are free to change and redistribute it.\n\
There is NO WARRANTY, to the extent permitted by law.'

    program = CommandLineApp(
        program_description=PROGRAM_DESCRIPTION.replace('\t', ''),
        program_license=PROGRAM_LICENSE.replace('\t', ''),
        version_string='0.1',
        year_string='2020',
        author_name='Ljubomir Kurij',
        author_mail='ljubomir_kurij@protonmail.com',
        epilogue=None)

    program.add_argument_group('general options')
    program.add_argument(
        '-V',
        '--version',
        action='store_true',
        help='print program version',
        group='general options')
    program.add_argument(
        '--usage',
        action='store_true',
        help='give a short usage message')
    program.add_argument(
        '-d', '--delimiter',
        action='store',
        metavar='DELIMITER',
        type=str,
        help='field delimiter. Default value is \",\"',
        group='general options')
    program.add_argument(
        'data_file',
        metavar='DATA_FILE',
        type=str,
        nargs='?',
        help='a CSV file containing graph data')

    program.parse_args()
    program.run()
