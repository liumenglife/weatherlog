# -*- coding: utf-8 -*-


# This file defines functions used for uploading data to pastebin.


# Import urlopen and urlencode for making requests.
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import URLError
except ImportError:
    from urllib import urlopen, urlencode
    from urllib2 import URLError
# Import json and export for converting data format.
import json
import weatherlog_resources.export as export
# Import application constants.
from weatherlog_resources.constants import *


def upload_pastebin(data, name, mode, expires, exposure, units, config, title):
    """Uploads the data to pastebin."""
    
    # Load the constants file.
    try:
        const_file = open("weatherlog_resources/appdata/pastebin.json", "r")
        const_data = json.load(const_file)
        expires_dict = const_data["expires"]
        exposure_dict = const_data["exposure"]
        const_file.close()
    
    except IOError as e: 
        print("upload_pastebin(): Error reading pastebin constants file (IOError):\n%s" % e)
        return PastebinExport.NO_CONSTANTS, False
    
    # Convert the data.
    if mode == "html":
        data_list = [[title,
                     ["Date", "Temperature (%s)" % units["temp"], "Wind Chill (%s)" % units["temp"],
                      "Precipitation (%s)" % units["prec"], "Wind (%s)" % units["wind"],
                      "Humidity (%%)", "Air Pressure (%s)" % units["airp"], "Visibility (%s)" % units["visi"],
                      "Cloud Cover", "Notes"],
                      data]]
        new_data = export.html_generic(data_list)
    elif mode == "csv":
        new_data = export.csv(data, units)
    elif mode == "json":
        new_data = json.dumps(data)
    
    # Build the api string.
    api = {"api_option": "paste",
           "api_dev_key": config["pastebin"],
           "api_paste_private": exposure_dict[exposure],
           "api_paste_expire_date": expires_dict[expires],
           "api_paste_code": new_data}
    print(expires_dict[expires])
    if mode == "html":
        api["api_paste_format"] = "html5"
    elif mode == "raw":
        api["api_paste_format"] = "javascript"
    
    if name.lstrip().rstrip() == "":
        api["api_paste_name"] = config["pastebin_default_name"]
    else:
        api["api_paste_name"] = name.lstrip().rstrip()
    
    # Upload the text.
    try:
        print(api)
        pastebin = urlopen("http://pastebin.com/api/api_post.php", urlencode(api))
        result = pastebin.read()
        pastebin.close()
        
        # Check for an error message.
        if "invalid api_dev_key" in result:
            return PastebinExport.INVALID_KEY, False
        else:
            return PastebinExport.SUCCESS, result
        
    except IOError as e:
        return PastebinExport.ERROR, "Could not connect to Pastebin."
