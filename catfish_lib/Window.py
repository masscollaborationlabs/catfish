#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#   Catfish - a versatile file searching tool
#   Copyright (C) 2007-2012 Christian Dywan <christian@twotoasts.de>
#   Copyright (C) 2012-2014 Sean Davis <smd.seandavis@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License version 2, as published
#   by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranties of
#   MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk  # pylint: disable=E0611
import logging
logger = logging.getLogger('catfish_lib')

from . helpers import get_builder


def detach_cb(menu, widget):
    """Detach callback function for the AppMenu."""
    menu.detach()


def menu_position(self, menu, data=None, something_else=None):
    """Menu positioning function for the AppMenu."""
    widget = menu.get_attach_widget()
    allocation = widget.get_allocation()
    window_pos = widget.get_window().get_position()
    x = window_pos[0] + allocation.x - menu.get_allocated_width() + \
        widget.get_allocated_width()
    y = window_pos[1] + allocation.y + allocation.height
    return (x, y, True)


class Window(Gtk.Window):
    """This class is meant to be subclassed by CatfishWindow. It provides
    common functions and some boilerplate."""
    __gtype_name__ = "Window"

    # To construct a new instance of this method, the following notable
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing

    def __new__(cls):
        """Special static method that's automatically called by Python when
        constructing a new instance of this class.

        Returns a fully instantiated BaseCatfishWindow object.
        """
        builder = get_builder('CatfishWindow')
        new_object = builder.get_object("catfish_window")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a CatfishWindow object with it in order to finish
        initializing the start of the new CatfishWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)
        self.AboutDialog = None  # class

        self.sidebar = self.builder.get_object('sidebar')

        self.appmenu = self.builder.get_object('appmenu')
        self.appmenu_button = self.builder.get_object('appmenu_button')
        self.appmenu.attach_to_widget(self.appmenu_button, detach_cb)

    # Help not currently in use.
    #def on_mnu_contents_activate(self, widget, data=None):
    #    show_uri(self, "ghelp:%s" % get_help_uri())

    def on_mnu_about_activate(self, widget, data=None):
        """Display the about box for catfish."""
        if self.AboutDialog is not None:
            about = self.AboutDialog()  # pylint: disable=E1102
            about.run()
            about.destroy()

    def on_destroy(self, widget, data=None):
        """Called when the CatfishWindow is closed."""
        self.search_engine.stop()
        self.settings.write()
        Gtk.main_quit()

    def on_appmenu_button_clicked(self, widget):
        """When the menu button is clicked, display the appmenu."""
        if widget.get_active():
            self.appmenu.popup(None, None, menu_position,
                               self.appmenu, 3,
                               Gtk.get_current_event_time())

    def on_appmenu_hide(self, widget):
        """Unclick the appmenu button when the menu is hidden."""
        self.appmenu_button.set_active(False)

    def on_catfish_window_window_state_event(self, widget, event):
        """Properly handle window-manager fullscreen events."""
        self.window_is_fullscreen = bool(event.new_window_state &
                                         Gdk.WindowState.FULLSCREEN)

    def on_catfish_window_key_press_event(self, widget, event):
        """Handle keypresses for the Catfish window."""
        key_name = Gdk.keyval_name(event.keyval)
        if key_name == 'F9':
            self.sidebar_toggle_menu.activate()
            return True
        if key_name == 'F11':
            if self.window_is_fullscreen:
                self.unfullscreen()
            else:
                self.fullscreen()
            return True
        return False
