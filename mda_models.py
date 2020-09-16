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
# * mda_models.py: created.
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

from sys import float_info as fi  # Required by MIN_FLOAT and MAX_FLOAT
from collections import namedtuple
import csv
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

def _checktype(tpe, var, vardsc):
    """ Utility routine used to check if given variable (var) is of requested
    type (tpe). If not it raises TypeError exception with an appropriate
    error message.
    """

    if var is not None and not isinstance(var, tpe):
        raise TypeError('{0} must be {1} or NoneType, not {2}'.format(
            vardsc,
            tpe.__name__,
            type(var).__name__
        ))


ReadErrorType = namedtuple('ReadErrorType', 'EMPTY_FILE NO_DATA \
    TOO_MANY_COLUMNS ROW_WIDTH_TOO_SMALL ROW_WIDTH_TOO_BIG')


ReadError = ReadErrorType(
    EMPTY_FILE='Empty file',
    NO_DATA='No table data could be found',
    TOO_MANY_COLUMNS='Too many data columns',
    ROW_WIDTH_TOO_SMALL='Row width too small',
    ROW_WIDTH_TOO_BIG='Row width too big'
    )


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
            self.errors.append((0, self.last_error))

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
                self.errors.append((0, self.last_error))
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
# Model classes
# =============================================================================

class Graph():
    """TODO: Put class docstring HERE.
    """

    def __init__(self, data, headers):
        self._data = dict()
        self._data['headers'] = headers
        self._data['raw'] = data

    @property
    def headers(self):
        """TODO: Put method docstring HERE.
        """

        # TODO: Generate headers if None.
        return self._data['headers']

    @property
    def data(self):
        """TODO: Put method docstring HERE.
        """

        return self._data['raw']

    def scaled_window_smoothed(
            self,
            data_array,
            win_type='hanning',
            win_len=11
            ):
        """Smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the
        signal (data array). The signal is prepared by introducing reflected
        copies of the signal (with the window size) in both ends so that
        transient parts are minimized in the begining and end part of the
        output array.

        Input:
            data_array: 1D numpy array storing data to be smoothed.

            win_type:   The type of window. Can have one of the following
                        values:
                            'flat',
                            'hanning',
                            'hamming',
                            'bartlett',
                            'blackman'.

                        Flat window will produce a moving average smoothing.

            win_len:    The length of the smoothing window. Should be an
                        odd integer.

        Result:
            The smoothed 1D data array.

        Notes:
            * Input data data array needs to be bigger than window
              size (win_len).
        """

        if data_array.size < win_len:
            raise ValueError(
                'Input vector needs to be bigger than window size.'
                )

        if win_len < 3:
            return data_array

        win_types = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        if win_type not in win_types:
            raise ValueError(
                'Scaled window type must be one of "flat", "hanning", \
                "hamming", "bartlett", "blackman"'
                )

        reflected = np.r_[
            data_array[win_len-1:0:-1],
            data_array,
            data_array[-2:-win_len-1:-1]
            ]

        window = None
        if win_type == 'flat':  # moving average
            window = np.ones(win_len, 'd')
        elif win_type == 'hanning':
            window = np.hanning(win_len)
        elif win_type == 'hamming':
            window = np.hamming(win_len)
        elif win_type == 'bartlett':
            window = np.bartlett(win_len)
        else:  # It must be 'blackman'.
            window = np.blackman(win_len)

        result = np.convolve(window / window.sum(), reflected, mode='valid')

        # Because len(output) != len(input) we don't simply return result,
        # but a ...
        return result[(win_len/2-1):-(win_len/2)]
