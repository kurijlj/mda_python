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
# * mda_views.py: created.
#
# =============================================================================


# ============================================================================
#
# TODO: Implement named tuple for passing smoothing options preview.
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

from enum import Enum  # Required by Message class.
from matplotlib import use  # Required by use in line 63
from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk
    )
import tkinter as tki
import tkinter.ttk as ttk
import matplotlib.pyplot as plt

use("TkAgg")
plt.style.use('bmh')


# =============================================================================
# Utility classes and functions
# =============================================================================

class Message(Enum):
    """An utility class to enumarate messages that can be exchanged between GUI
    elements via mediator (controller) object.
    """

    updtview = 0  # Update view.
    smchngd = 1   # Graph smoothing options have changed.

def checktype(tpe, var, vardsc):
    """Utility routine used to check if given variable (var) is of requested
    type (tp). If not it raises TypeError exception with a appropriate message.
    Variable description (vardsc) is used for formatting more descriptive error
    messages on rising exception.
    """

    if var is not None and type(var) is not tpe:
        raise TypeError('{0} must be {1} or NoneType, not {2}'.format(
            vardsc,
            tpe.__name__,
            type(var).__name__
        ))


# =============================================================================
# View classes
# =============================================================================

class PlotNavigationToolbar(NavigationToolbar2Tk):
    """ TODO: Put class docstring HERE.
    """

    def __init__(self, canvas, window):
        # Pass initialization to the superclass.
        super().__init__(canvas, window)

    def mouse_move(self, event):
        """ TODO: Put method docstring HERE.
        """

        # We don't want any position message in the toolbar.
        self.set_message('')


class PlotView(tki.Frame):
    """ Custom widget base class for displaying matlplotlib plot.
    """

    def __init__(self, *args, **kwargs):

        # Reference to a controller object must be passed as key-word agrument.
        if 'controller' in kwargs:
            self._controller = kwargs.pop('controller')
        else:
            # No reference to controller object.
            self._controller = None

        # Graph's line width value (linewidth) must be passed as
        # key-word agrument.
        if 'linewidth' in kwargs:
            self._linewidth = kwargs.pop('linewidth')
        else:
            # Set default line thickness for the plot.
            self._linewidth = 0.5

        # Pass the rest of initialization to the superclass.
        tki.Frame.__init__(self, *args, **kwargs)

        # Initialize the figure.
        self._figure = plt.Figure()
        FigureCanvasTkAgg(self._figure, self)
        self._figure.canvas.get_tk_widget().pack(fill=tki.BOTH, expand=True)
        self._figure.canvas.draw()

        # Initialize axes.
        self._axes = self._figure.add_subplot(111)

        # Add toolbar so user can zoom, take screenshots, etc.
        self._toolbar = PlotNavigationToolbar(
                self._figure.canvas,
                self,
            )
        self._toolbar.pack_propagate(0)

        # Update toolbar display.
        self._toolbar.update()

        # Initialize smoothing options preview.
        smth_modes = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        self._smth_prvu = dict()
        for mode in smth_modes:
            self._smth_prvu[mode] = False

    def change_smoothing_preview(self, options):
        """TODO: Put method docstring HERE.
        """

        self._smth_prvu = options
        self._update()

    def model(self):
        """TODO: Put method docstring HERE.
        """

        model = None
        if self._controller and hasattr(self._controller, 'data_model'):
            model = self._controller.data_model
        return model

    def _update(self):
        """ TODO: Put method docstring HERE.
        """

        model = self.model()

        # First clear axes.
        self._axes.clear()

        if model is not None:
            self._axes.plot(
                model.data[:, 1],
                '-',
                linewidth=self._linewidth,
                label='Measured Data',
                )

            for mode in self._smth_prvu:
                if self._smth_prvu[mode]:
                    self._axes.plot(
                        model.scaled_window_smoothed(
                            model.data[:, 1],
                            win_type=mode
                            ),
                        '-',
                        linewidth=self._linewidth,
                        label=mode.capitalize()
                        )
            self._axes.set_xlabel(model.headers[0])
            self._axes.set_ylabel(model.headers[1])
            self._axes.set_title(model.title)
            self._axes.legend()

        self._figure.canvas.draw()

        # Update superclass.
        tki.Tk.update(self)

    def update(self):
        """ TODO: Put method docstring HERE.
        """

        self._update()


class AppControlsView(tki.Frame):
    """ Custom widget class for displaying and taking input from user
    controlls (e.g. radiobuttonsw, etc.).
    """

    def __init__(self, *args, **kwargs):

        # Reference to a controller object must be passed as key-word agrument.
        # Controller object's class must implement dispatch method takeing
        # following arguments dispatch(sender, message, **kwargs).
        if 'controller' in kwargs:
            self.controller = kwargs.pop('controller')
            if not self.controller or not hasattr(self.controller, 'dispatch'):
                raise TypeError(
                        'Dispatch method not implemented by'
                        ' object\'s class ({0}).'
                        .format(type(self.controller))
                    )
        else:
            # No reference to controller object.
            self.controller = None

        # Reference to the root widget must be passed as key-word agrument.
        if 'mainwindow' in kwargs:
            self._mainwindow = kwargs.pop('mainwindow')
        else:
            # No reference to the root widget.
            self._mainwindow = None

        # Pass the rest of initialization to the superclass.
        tki.Frame.__init__(self, *args, **kwargs)

        # Set label frame to distinct control panel from the rest of the GUI.
        labelframe = ttk.LabelFrame(self, text='Control Panel')
        labelframe.pack(side=tki.RIGHT, fill=tki.Y, padx=5, pady=5)

        # Split control view into upper and lower half. Upper one is to hold
        # actual display controls, while lower one holds 'Quit' button only.
        top_frame = ttk.Frame(labelframe)
        top_frame.pack(side=tki.TOP, fill=tki.X, padx=5, pady=5)
        spacer = ttk.Frame(labelframe)
        spacer.pack(side=tki.TOP, fill=tki.Y, expand=True)
        bottom_frame = ttk.Frame(labelframe)
        bottom_frame.pack(side=tki.BOTTOM, fill=tki.X, padx=5, pady=5)

        # Set smoothing controls. First set dictionary to keep track of
        # user selected smoothing options for the plotted data.
        smth_modes = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        self._smoothing = dict()
        for mode in smth_modes:
            self._smoothing[mode] = tki.BooleanVar()
            ttk.Checkbutton(
                    top_frame,
                    text=mode.capitalize(),
                    command=self._toggle_smth_mode,
                    variable=self._smoothing[mode]
                ).pack(side=tki.TOP, fill=tki.X)
            self._smoothing[mode].set(0)

        # Set appllication "Quit" button.
        destroycmd = None
        if self._mainwindow and hasattr(self._mainwindow, 'destroy'):
            destroycmd = self._mainwindow.destroy

        ttk.Button(bottom_frame, text='Quit', command=destroycmd)\
            .pack(side=tki.TOP, fill=tki.X)

    def _toggle_smth_mode(self):
        """Method to be called when one of smoothing radio buttons is
        checked. It invokes actual method that turns mode display on/off.
        """

        if hasattr(self.master, 'dispatch'):
            self.controller.dispatch(
                self,
                Message.smchngd,
                smoothing=self._smoothing
                )


class TkiAppMainWindow(tki.Tk):
    """ Application's main window.
    """

    def __init__(self, *args, **kwargs):

        tki.Tk.__init__(self, className='TkiAppMAinWindow')

        # Since objects instantiated from class are intended to be top level
        # widgets there is no reason to pass reference to master object.

        # Reference to a controller object must be passed as key-word agrument.
        if 'controller' in kwargs:
            self._controller = kwargs['controller']
        else:
            # No reference to controller object.
            self._controller = None

        self.resizable(True, True)
        # self.resizable(False, False)

        # Set up main frame with the label.
        main_panel_frame = ttk.LabelFrame(
                self,
                text='Main Widget Panel',
                borderwidth=3
                )

        # Pack top container widget.
        main_panel_frame.pack(
            side=tki.LEFT,
            fill=tki.BOTH,
            expand=True,
            padx=2,
            pady=2
            )

        # ======================================================================
        # Place your widgets here.
        # ======================================================================

        self._plot_view = PlotView(
            main_panel_frame,
            controller=self._controller
            )
        self._plot_view.pack(side=tki.TOP, fill=tki.BOTH, expand=True)

        # ======================================================================

        # Set up some space between test widgets and control widgets.
        ttk.Frame(main_panel_frame).pack(
            side=tki.LEFT,
            fill=tki.Y,
            pady=4
            )

        # Set up control widgets and pack.
        self._controlpanel = AppControlsView(
                self,
                controller=self,
                mainwindow=self
            )
        self._controlpanel.pack(side=tki.RIGHT, fill=tki.Y)

    def _update(self):
        """Method to update display of main window.
        """
        self._plot_view.update()

    def dispatch(self, sender, event, **kwargs):
        """A method to mediate messages between GUI objects and GUI objects
        and the controller.
        """

        # So far we send all messages to the controller.
        # self.controller.dispatch(sender, event, **kwargs)
        if event == Message.smchngd:
            if 'smoothing' in kwargs:
                options = dict()
                for mode in kwargs['smoothing']:
                    options[mode] = kwargs['smoothing'][mode].get()
                self._plot_view.change_smoothing_preview(options)

            else:
                print('{0}: \'smoothing\' parameter is missing.'
                      .format(self._programName))

    def update(self):
        """TODO: Put method docstring HERE.
        """

        self._update()
        tki.Tk.update(self)
