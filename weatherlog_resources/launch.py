# -*- coding: utf-8 -*-


# This file defines the functions for launching and setting up the application.


# Import json for loading and saving the data.
import json
# Import platform for getting the user's operating system.
import platform
# Import os for creating a directory and other tasks.
import os
# Import sys for closing the application.
import sys
# Import glob for getting a list of directories.
import glob
# Import datetime for getting the current time.
import datetime
# Import pickle for loading and saving the data.
try:
    import cPickle as pickle
except ImportError:
    import pickle


def get_main_dir():
    """Returns the main directory."""

    # Windows:
    # * Data: C:\Users\[username]\AppData\Local\weatherlog
    # * Config: C:\Users\[username]\AppData\Local\weatherlog
    # Linux:
    # * Data: /home/[username]/.share/local/weatherlog
    # * Config: /home/[username]/.config/weatherlog/
    # OSX: probably the same as Linux?
    if platform.system().lower() == "windows":
        return os.environ["LOCALAPPDATA"] + "\weatherlog", os.environ["LOCALAPPDATA"] + "\weatherlog"
    else:
        base = os.path.expanduser("~")
        return base + "/.local/share/weatherlog", base + "/.config/weatherlog"


def get_ui_info():
    """Get the application's UI info."""
    
    try:
        ui_file = open("weatherlog_resources/appdata/ui.json", "r")
        ui_data = json.load(ui_file)
        ui_file.close()
    
    except IOError as e: 
        print("get_ui_info(): Error reading UI file (IOError):\n%s" % e)
        sys.exit()
    
    try:
        menu_file = open("weatherlog_resources/appdata/menu.xml", "r")
        menu_data = menu_file.read()
        menu_file.close()
    
    except IOError as e:
        print("get_ui_info(): Error reading menu file (IOError):\n%s" % e)
        sys.exit()
    
    version = ui_data["version"]
    title = ui_data["title"]
    icon_small = ui_data["icon_small"]
    icon_medium = ui_data["icon_medium"]
    icon_medium_about = ui_data["icon_medium_about"]
    default_width = ui_data["default_width"]
    default_height = ui_data["default_height"]
    help_link = ui_data["help_link"]
    return version, title, menu_data, icon_small, icon_medium, default_width, default_height, help_link


def get_weather_codes():
    """Get the weather codes."""
    
    try:
        codes_file = open("weatherlog_resources/appdata/weather_codes.json", "r")
        codes = json.load(codes_file)
        codes_file.close()
    
    except IOError as e: 
        print("get_weather_codes(): Error reading weather codes file (IOError):\n%s" % e)
        sys.exit()
    
    return codes


def check_files_exist(main_dir, conf_dir):
    """Checks to see if the base files exist, and create them if they don't."""

    # Check to see if the data directory exists, and create it if it doesn't.
    if not os.path.exists(main_dir) or not os.path.isdir(main_dir):

        # Create the default data directory and files.
        os.makedirs(main_dir)
        os.makedirs("%s/profiles/Main Dataset" % main_dir)
        last_prof_data = open("%s/profiles/Main Dataset/weather" % main_dir, "w")
        pickle.dump([], last_prof_data)
        last_prof_data.close()
        create_metadata(main_dir, "Main Dataset")

    # Check to see if the configuration directory exists, and create it if it doesn't.
    if not os.path.exists(conf_dir) or not os.path.isdir(conf_dir):

        # Create the default configuration directory and files.
        os.makedirs(conf_dir)
        last_prof = open("%s/lastprofile" % conf_dir, "w")
        last_prof.write("Main Dataset")
        last_prof.close()


def get_config(conf_dir, get_default = False):
    """Loads the settings."""
    
    # Get the default configuration.
    try:
        default_config_file = open("weatherlog_resources/appdata/default_config.json", "r")
        default_config = json.load(default_config_file)
        default_config_file.close()
    
    except IOError as e:
        print("get_config(): Error reading default config file (IOError):\n%s" % e)
        sys.exit()

    # Get the configuration.
    try:
        config_file = open("%s/config.json" % conf_dir, "r")
        config = json.load(config_file)
        config_file.close()

    except IOError as e:
        # If there was an error, use the defaults instead.
        print("get_config(): Error reading config file (IOError):\n%s\nContinuing with default..." % e)
        config = default_config
    
    if get_default:
        config = default_config
    
    return config


def get_restore_data(main_dir, conf_dir, config, default_width, default_height, default_profile = "Main Dataset"):
    """Gets the last window size."""

    # Otherwise, get the previous window size.
    try:
        rest_file = open("%s/application_restore.json" % conf_dir, "r")
        rest_data = json.load(rest_file)
        rest_file.close()
        last_width = rest_data["window_width"]
        last_height = rest_data["window_height"]
        last_profile = rest_data["last_dataset"]

    except IOError as e:
        # If there was an error, use the default data instead.
        print("get_window_size(): Error reading application restore file (IOError):\n%s\nContinuing with default..." % e)
        last_width = default_width
        last_height = default_height
        last_profile = default_profile
    
    # Get the list of datasets.
    current_dir = os.getcwd()
    os.chdir("%s/profiles" % main_dir)
    profiles_list = glob.glob("*")
    os.chdir(current_dir)

    # Check if the dataset exists:
    if last_profile in profiles_list:
        profile_exists = True
        original_profile = ""
    else:
        profile_exists = False
        original_profile = last_profile
    
    # If the dataset doesn't exist, switch or make one that does:
    if not profile_exists:

        # If the default dataset exists, switch to that.
        if "Main Dataset" in profiles_list:
            last_profile = "Main Dataset"

        # Otherwise, create the dataset:
        else:

            # Create the Main Dataset directory and data file.
            os.makedirs("%s/profiles/Main Dataset" % main_dir)
            last_prof_data = open("%s/profiles/Main Dataset/weather" % main_dir, "w")
            pickle.dump([], last_prof_data)
            last_prof_data.close()
            create_metadata(main_dir, "Main Dataset")

            # Set the dataset name.
            last_profile = "Main Dataset"
    
    # If the user doesn't want to restore the window size, set the size to the defaults.
    if not config["restore"]:
        return last_profile, original_profile, profile_exists, default_width, default_height

    return last_profile, original_profile, profile_exists, last_width, last_height


def get_units(config):
    """Gets the units."""
    
    # Get the units.
    try:
        units_file = open("weatherlog_resources/appdata/units.json", "r")
        units = json.load(units_file)
        units_file.close()
    
    except IOError as e:
        print("get_units(): Error reading units file (IOError):\n%s" % e)
        sys.exit()
    
    return units[config["units"]]


def get_data(main_dir, last_profile):
    """Gets the data."""

    try:
        # Load the data.
        data_file = open("%s/profiles/%s/weather" % (main_dir, last_profile), "r")
        data = pickle.load(data_file)
        data_file.close()

    except IOError as e:
        print("get_data(): Error importing data (IOError):\n%s" % e)
        sys.exit()

    except (TypeError, ValueError) as e:
        print("get_data(): Error importing data (TypeError or ValueError):\n%s" % e)
        sys.exit()

    return data


def create_metadata(main_dir, last_profile):
    """Creates the default metadata file."""

    # Get the current time.
    now = datetime.datetime.now()
    modified = "%d/%d/%d" % (now.day, now.month, now.year)

    # Write the metadata to the file.
    try:
        meta_file = open("%s/profiles/%s/metadata.json" % (main_dir, last_profile), "w")
        json.dump({"creation": modified, "modified": modified}, meta_file)
        meta_file.close()

    except IOError as e:
        print("create_metadata(): Error saving metadata file (IOError):\n%s" % e)


def get_pastebin_constants():
    """Gets the Pastebin constants."""
    
    # Get the units.
    try:
        paste_file = open("weatherlog_resources/appdata/pastebin.json", "r")
        paste_constants = json.load(paste_file)
        paste_file.close()
    
    except IOError as e:
        print("get_pastebin_constants(): Error reading pastebin constants file (IOError):\n%s" % e)
        sys.exit()
    
    return paste_constants
