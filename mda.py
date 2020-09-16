#!/usr/bin/env python
"""TODO: Put module docstring HERE.
"""

# ============================================================================
# Copyright (C) 2020 Ljubomir Kurij <kurijlj@gmail.com>
#
# This file is part of mda (Measurement Data Analytics).
#
# <program name> is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ============================================================================


# ============================================================================
#
# 2020-08-31 Ljubomir Kurij <kurijlj@gmail.com>
#
# * mda.py: created.
#
# ============================================================================


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

from os.path import isfile
from sys import float_info as fi  # Required by MIN_FLOAT and MAX_FLOAT
import csv
import argparse
import numpy as np


# =============================================================================
# Global constants
# =============================================================================

# Centimeters per inch.
CM_PER_IN = 2.54
MM_PER_IN = 25.4

MIN_FLOAT = fi.min
MAX_FLOAT = fi.max


# =============================================================================
# Utility classes and functions
# =============================================================================

class ProgramAction():
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


def _format_epilog(epilogue_addition, bug_mail):
    """Formatter for generating help epilogue text. Help epilogue text is an
    additional description of the program that is displayed after the
    description of the arguments. Usually it consists only of line informing
    to which email address to report bugs to, or it can be completely
    omitted.

    Depending on provided parameters function will properly format epilogue
    text and return string containing formatted text. If none of the
    parameters are supplied the function will return None which is default
    value for epilog parameter when constructing parser object.
    """

    fmt_mail = None
    fmt_epilogue = None

    if epilogue_addition is None and bug_mail is None:
        return None

    if bug_mail is not None:
        fmt_mail = 'Report bugs to <{bug_mail}>.'.format(bug_mail=bug_mail)
    else:
        fmt_mail = None

    if epilogue_addition is None:
        fmt_epilogue = fmt_mail

    elif fmt_mail is None:
        fmt_epilogue = epilogue_addition

    else:
        fmt_epilogue = '{addition}\n\n{mail}'.format(
            addition=epilogue_addition,
            mail=fmt_mail
            )

    return fmt_epilogue


def _formulate_action(action, **kwargs):
    """Factory method to create and return proper action object.
    """

    return action(**kwargs)


# =============================================================================
# Data classes
# =============================================================================


class ReadError():
    """TODO: Put class docstring HERE.
    """

    EMPTY_FILE = 'Empty file'
    NO_DATA = 'No table data could be found'
    TOO_MANY_COLUMNS = 'Too many data columns'
    ROW_WIDTH_TOO_SMALL = 'Row width too small'
    ROW_WIDTH_TOO_BIG = 'Row width too big'


class CSVDataReader():
    """TODO: Put class docstring HERE.
    """

    def __init__(self, max_col_count=26):
        # Set maximum allowed column count per dataset to 26.
        self.max_col_count = max_col_count

        # Initialize attributes.
        self.file_name = None  # Name of file containing data.
        self.headers = None  # Tuple holding data column headers.
        self.error_count = 0  # Counts errors encountered while reading data.
        self.errors = list()  # Map of row numbers and encountered errors.
        self.last_error = None  # Last encountered error string.
        self.row_count = -1  # Number of red rows.
        self.column_count = -1  # Number of red columns.

    def _clear_error_log(self):
        """Resets all error attributes and prepares reader for new reading.
        """

        self.file_name = None
        self.headers = None
        self.error_count = 0
        self.errors = list()
        self.last_error = None
        self.row_count = -1
        self.column_count = -1

    def _is_empty(self, data_file):
        """Tests if passed file contains any data at all.

        It returns True if file is empty, othervise returns False.
        """

        state = False

        # Save current position of the read/write pointer and move pointer to
        # the beginning of the file.
        old_pos = data_file.tell()
        data_file.seek(0)

        # Read first character.
        one_char = data_file.read(1)

        # If not fetched then file is empty.
        if not one_char:
            state = True
            self.error_count += 1
            self.last_error = ReadError.EMPTY_FILE
            self.errors.append((0, self.last_error))

        # Restore file pointer position.
        data_file.seek(old_pos)

        return state

    def _has_header(self, data_file):
        """Check if given CSV file contains column header by means of calling
        has_header() method of the Sniffer class from csv module.

        It returns True if file has a header, othervise returns False.
        """

        state = False

        # Save current position of the read/write pointer and move pointer to
        # the beginning of the file.
        old_pos = data_file.tell()
        data_file.seek(0)

        try:
            state = csv.Sniffer().has_header(data_file.read(1024))

        except csv.Error as err:
            self.error_count += 1
            self.last_error = err
            self.errors.append((0, self.last_error))

        # Restore file pointer position.
        data_file.seek(old_pos)

        return state

    def _data_shape(self, data_file, delimiter):
        """Counts rows and columns of the given file.

        It returns tuple of format (row_count, column_count).
        """

        row_count = 0
        column_count = 0

        # Save current position of the read/write pointer and move pointer to
        # the beginning of the file.
        old_pos = data_file.tell()
        data_file.seek(0)

        datareader = csv.reader(data_file, delimiter=delimiter)
        for row in datareader:
            # If this is first row beeing red count number of fields it
            # contains and use that number as number of columns in the dataset.
            if row_count == 0:
                column_count = len(row)

            # For each row in datareader increase counter by one.
            row_count += 1

        # Restore file pointer position.
        data_file.seek(old_pos)

        # If file has header we have to decrease row count  by one.
        if self._has_header(data_file):
            row_count -= 1

        # If either of the row_count or column_count is equal to 0 we consider
        # take the data set as empty.
        if row_count < 1 or column_count < 1:
            self.error_count += 1
            self.last_error = ReadError.NO_DATA
            self.errors.append(0, self.last_error)

        return (row_count, column_count)

    def read_data(self, file_name, delimiter=','):
        """Tries to read CSV data from a file designated with a passed file
        name.

        It returns two dimensional array representing data set. If the data set
        contains header it is stored in the header attribute of the
        CSVDataReader instance.

        If it encounters errors while reading file it returns None and propper
        error log is set. This error log can be exained by error_count, errors
        and last_error attributes, where:
            1. error_count represents number of errors encountered while
            reading file;
            2. errors is dictionary representing map of the error strings of
            encountered errors with indexes (starting from 1) of rows in the
            file beeing red where the errors have occured. If the error have
            occured in the header error string is mapped to the zero;
            3. last_error is an error string of the last encountered error.
        """

        # Reset attributes and clear error log.
        self._clear_error_log()
        self.file_name = file_name

        # Initialize data container.
        data = None

        with open(self.file_name) as data_file:
            # If f is an empty file abort further reading.
            if self._is_empty(data_file):
                return data

            # Try to determina data set shape (number of rows and columns).
            self.row_count, self.column_count = self._data_shape(
                data_file,
                delimiter
                )

            # If f is an empty data set abort further reading.
            if self.row_count < 1 or self.column_count < 1:
                return data

            has_header = self._has_header(data_file)

            # Since we don't process data sets with more columns than
            # number of columns set on the intialization of the
            # instance (max_col_count), check if column_count is
            # greater than set limit. If not continue with reading
            # the file, othervise set error log and abort further
            # reading.
            if self.max_col_count < self.column_count:
                self.error_count += 1
                self.last_error = ReadError.TOO_MANY_COLUMNS
                self.errors.append(0, self.last_error)
                return data

            # Allocate memory for storing data.
            data = np.zeros(
                (self.row_count, self.column_count),
                dtype=float
                )

            datareader = csv.reader(data_file, delimiter=delimiter)
            row_index = 0  # Row index.

            for row in datareader:
                if has_header and row_index == 0:
                    self.headers = tuple(row)

                else:
                    # Check row width, measured in number of fields. If row
                    # has less or more fileds than column_count, assume
                    # error and skip reading the row. Fill row fields in the
                    # data table with MIN_FLOAT.
                    if self.column_count != len(row):
                        if self.column_count > len(row):
                            self.last_error = ReadError.ROW_WIDTH_TOO_SMALL

                        else:
                            self.last_error = ReadError.ROW_WIDTH_TOO_BIG

                        self.error_count += 1
                        self.errors.append((row_index + 1, self.last_error))

                        # Column index.
                        for column_index in range(self.column_count):
                            data[row_index - 1, column_index] = MIN_FLOAT

                    else:
                        # Column index.
                        for column_index in range(self.column_count):
                            try:
                                data[
                                    row_index - 1,
                                    column_index
                                    ] = float(row[column_index])

                            # If we encounter error converting data set field
                            # into float fill that field in data table with
                            # the MIN_FLOAT.
                            except ValueError as err:
                                self.error_count += 1
                                self.last_error = err
                                self.errors.append((
                                    row_index + 1,
                                    self.last_error
                                    ))
                                data[row_index - 1, column_index] = MIN_FLOAT

                row_index += 1  # Increase row index.

        return data

    def print_error_report(self):
        """Prints summary error report of encountered errors to the stdout.
        """

        if not self.file_name:
            # No file was red or reader state was reset.
            print('No file was red.')
            return  # Bail out.

        print(
            'Summary of reading file \'{0}\':'
            .format(self.file_name)
            )
        print(
            '================================================================='
            + '==============\n'
            )
        if self.error_count:
            print(
                'Errors encountered: {0}.'
                .format(self.error_count)
                )
            print(
                'Last encountered error: {0}.'
                .format(self.last_error)
                )
            for error in self.errors:
                print('Row {0}: {1}.'.format(error[0], error[1]))

        else:
            print('No errors encountered.')


def print_to_stdout(data, headers=None):
    """TODO: Put function docstring HERE.
    """

    row_count, column_count = data.shape
    row_index, column_index = 0, 0

    # Generate columns headers if none.
    if not headers:
        headers = list()
        for column_index in range(column_count):
            headers.append('Column ' + str(column_index + 1))

    # Reset column index.
    column_index = 0

    # Print header.
    print('Row\t', end='')
    for column_title in headers:
        print(column_title + '\t', end='')
    print('')

    # Print data.
    for row_index in range(row_count):
        print(str(row_index + 1) + '\t', end='')
        for column_index in range(column_count):
            print(str(data[row_index, column_index]) + '\t', end='')
        print('')


# =============================================================================
# Command line app class
# =============================================================================

class CommandLineApp():
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
                epilog=None
            ):

        self.program_license = program_license
        self.version_string = version_string
        self.year_string = year_string
        self.author_name = author_name
        self.author_mail = author_mail

        fmt_epilogue = _format_epilog(epilog, author_mail)

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

            kwargsr = {k: kwargs[k] for k in kwargs.keys() if 'group' != k}
            group.add_argument(*args, **kwargsr)

    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of a parser object. It also
        instantiates action object that will be executed based on a
        input from command line.
        """

        arguments = self._parser.parse_args(args, namespace)

        if arguments.usage:
            self._action = _formulate_action(
                ProgramUsageAction,
                parser=self._parser,
                exitf=self._parser.exit)

        elif arguments.version:
            self._action = _formulate_action(
                ShowVersionAction,
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

            self._action = _formulate_action(
                    DefaultAction,
                    prog=self._parser.prog,
                    exitf=self._parser.exit,
                    data_file=arguments.data_file,
                    delimiter=delimiter
                )

    def run(self):
        """This method executes action code.
        """

        self._action.execute()


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

        data_reader = CSVDataReader()
        print(
            '{0}: Reading file \'{1}\'.\n\n'
            .format(self._program_name, self._data_file)
            )
        data = data_reader.read_data(self._data_file, self._delimiter)
        headers = data_reader.headers
        data_reader.print_error_report()
        print('\n')

        self._exit_app()


# =============================================================================
# Script main body
# =============================================================================

if __name__ == '__main__':
    program = CommandLineApp(
        program_description='Small Python script used to inspaect \
            and analyse 2D graph data.\n\
            Mandatory arguments to long options are mandatory for \
            short options too.'.replace('\t', ''),
        program_license='License GPLv3+: GNU GPL version 3 or later \
            <http://gnu.org/licenses/gpl.html>\n\
            This is free software: you are free to change and \
            redistribute it.\n\
            There is NO WARRANTY, to the extent permitted by \
            law.'.replace('\t', ''),
        version_string='0.1',
        year_string='2020',
        author_name='Ljubomir Kurij',
        author_mail='ljubomir_kurij@protonmail.com',
        epilog=None)

    program.add_argument_group('general options')
    program.add_argument(
            '-V', '--version',
            action='store_true',
            help='print program version'
        )
    program.add_argument(
            '--usage',
            action='store_true',
            help='give a short usage message'
        )
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

    program.parse_args()
    program.run()
