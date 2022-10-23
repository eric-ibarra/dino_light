import machine
import urequests as requests
import os
import ujson as json

DOWNLOAD_SUCCESS = 1
DOWNLOAD_FAIL = 0

def check_update_needed(server, current_version, mac_address):
    print('check for update at %s/update/version/%s' % (server, current_version))
    req = requests.get(url='%s/update/version/%s' % (server, current_version))
    if 'true' in req.text:
        return True
    else:
        return False

def download_app(server, app_files, mac=None):
    for current_file in app_files:
        if download_file('%s/firmware/%s' % (server, current_file)) == DOWNLOAD_FAIL and 'mqtt_config.py' not in current_file:
            print('downloading %s/firmware/%s' % (server, current_file))
            return

    # Rename all files once download is complete
    for current_file in app_files:
        output_filename = current_file.lstrip('%d_' % mac) if 'mqtt_config.py' in current_file else current_file
        os.rename('temp_ota_%s' % current_file, output_filename)

    # Reboot for changes to take effect
    machine.reset()

def download_file(url, retries=3):
    for i in range(0, retries):
        try:
            req = requests.get(url=url)
            filename = url.split('/')[-1]
            if req.status_code == 200:
                print('Sucess downloading %s'%filename)
                with open("temp_ota_%s" % filename, 'wb') as outfile:
                    outfile.write(req.content)
                return True
        except Exception as e:
            print(e)
        print('Unable to download file, retrying...')
    return False
