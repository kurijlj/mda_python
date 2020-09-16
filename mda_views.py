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

from matplotlib import use
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

        self._set_cursor(event)
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
                linewidth=0.5,
                color='green'
                )

        # Update superclass.
        tki.Tk.update(self)

    def update(self):
        """ TODO: Put method docstring HERE.
        """

        self._update()


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
        main_panel_frame.pack(side=tki.TOP, fill=tki.X, padx=2, pady=2)

        # ======================================================================
        # Place your widgets here.
        # ======================================================================

        self._plot_view = PlotView(
            main_panel_frame,
            controller=self._controller
            )
        self._plot_view.pack(side=tki.TOP, fill=tki.X)

        # ======================================================================

        # Set up some space between test widgets and control widgets.
        ttk.Frame(main_panel_frame).pack(side=tki.TOP, fill=tki.Y, expand=True)

        # Set up control widgets and pack.
        ttk.Button(main_panel_frame, text='Quit', command=self.destroy)\
            .pack(side=tki.BOTTOM, fill=tki.X, padx=1, pady=1)

    def _update(self):
        """Method to update display of main window.
        """
        self._plot_view.update()

    def update(self):
        """TODO: Put method docstring HERE.
        """

        self._update()
        tki.Tk.update(self)
