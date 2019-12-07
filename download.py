import os
import requests
import datetime
import pytz
from dateutil.parser import parse as parsedate
import wget
import data

def download_log(url, new_filename):
    filename = wget.download(url)
    os.rename(filename, new_filename)

def download_logs(urls):
    for url in urls:
        filename = wget.detect_filename(url)
        new_filename = "logs/" + data.filename_from_url(url)
        print "Checking log " + new_filename
        # If the path exists, check if there's a more up to date version and, if so, remove the old and download the new...
        if os.path.exists(new_filename):
            r = requests.head(url)
            if "last-modified" in r.headers:
                url_time = r.headers['last-modified']
                url_date = parsedate(url_time)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(new_filename))
                url_date = url_date.replace(tzinfo=None)
                file_time = file_time.replace(tzinfo=None)
                pytz.UTC.localize(url_date)
                pytz.UTC.localize(file_time)
                if url_date > file_time:    
                    os.remove(new_filename)
                    download_log(url, new_filename)
            else:
                os.remove(new_filename)
                download_log(url, new_filename)
        # ... otherwise we just download it without any checks.
        else:
            download_log(url, new_filename)

print "Downloading log files..."
download_logs(data.log_urls)