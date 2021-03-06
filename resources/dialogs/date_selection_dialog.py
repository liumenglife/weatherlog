# -*- coding: utf-8 -*-


################################################################################
#
# WeatherLog: dialogs/date_selection_dialog.py
# This dialog selects dates from a list.
#
################################################################################


# Import GTK for the dialog.
from gi.repository import Gtk


class DateSelectionDialog(Gtk.Dialog):
    """Shows the date selection dialog."""

    def __init__(self, parent, title, subtitle, dates, buttons=None,
                 default_button=Gtk.ResponseType.OK, show_conflicts=False, multi_select=True, import_mode=False):
        """Create the dialog."""

        Gtk.Dialog.__init__(self, title, parent, Gtk.DialogFlags.MODAL, use_header_bar=True)
        self.set_default_size(500, 200)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        if buttons is None:
            self.add_button("OK", Gtk.ResponseType.OK)
        else:
            for i in buttons:
                self.add_button(i[0], i[1])

        self.default_button = default_button

        # Create the header bar.
        header = self.get_header_bar()
        header.set_title(title)
        header.set_subtitle(subtitle)

        # Create the Date selection.
        if show_conflicts:
            self.liststore = Gtk.ListStore(str, str)
        else:
            self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        if not show_conflicts:
            self.treeview.set_headers_visible(False)
        if multi_select:
            self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        date_text = Gtk.CellRendererText()
        self.date_col = Gtk.TreeViewColumn("Date", date_text, text=0)
        self.date_col.set_expand(True)
        self.treeview.append_column(self.date_col)

        # Show the Conflict column, if required.
        if show_conflicts:
            conf_text = Gtk.CellRendererText()
            self.conf_col = Gtk.TreeViewColumn("Conflict", conf_text, text=1)
            self.conf_col.set_expand(True)
            self.treeview.append_column(self.conf_col)

        # Display the UI.
        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.set_vexpand(True)
        scrolled_win.set_hexpand(True)
        scrolled_win.add(self.treeview)
        self.get_content_area().add(scrolled_win)

        # Add the dates.
        if import_mode:
            for i in dates:
                if show_conflicts:
                    self.liststore.append(i)
                else:
                    self.liststore.append([i])
        else:
            for i in dates:
                self.liststore.append(i)

        # Connect 'Enter' key to the OK button.
        ok_btn = self.get_widget_for_response(response_id=default_button)
        ok_btn.set_can_default(True)
        ok_btn.grab_default()

        # Bind the events.
        self.treeview.connect("row-activated", self.activated_event)

        # Show the dialog.
        self.show_all()

    def activated_event(self, widget, treepath, column):
        """Opens the edit dialog on double click."""

        self.response(self.default_button)
