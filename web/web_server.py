import signal
import logging
import json
import os
import sys

import tornado.ioloop
import tornado.web
import tornado.options

import paho.mqtt.client as mqtt

MQTT_SERVER = 'localhost'

if sys.version_info[0] == 3:
    import asyncio
    if sys.platform.startswith('win32'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        MQTT_SERVER = 'killerbeez.ddns.net'

FIRMWARE_PATH = 'firmware'


class MyApplication(tornado.web.Application):
    is_closing = False

    def signal_handler(self, signum, frame):
        logging.info('exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            logging.info('exit success')

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("access-control-allow-origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        # HEADERS!
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

class MyHandler(BaseHandler):
    def put(self):
        print("some post")

    def get(self):
        self.write("Hello, world")

    def post(self):
        global actions
        #self.set_header("Content-Type", "text/plain")
        print(self.request.body)

        self.write(json.dumps(actions))
        print(actions)
        actions['Update'] = 0

class UpdateHandler(BaseHandler):
    def get(self, path):
        print(path)
        try:
            command, current_version = path.split('/')
            current_version = int(current_version)
            firmware_file = '%s/version.py' % FIRMWARE_PATH
            if os.path.exists(firmware_file):
                with open(firmware_file, 'r') as infile:
                    data = infile.read()
                version = int(data.split('=')[1])
                print('file version %s' % version)
                if version != current_version:
                    self.write('{"upgrade": true}')
                else:
                    self.write('{"upgrade": false}')
        except Exception as e:
            print(e)

    def post(self):
        try:
            device_config = json.loads(self.request.body)
            print(device_config)
        except Exception:
            logging.warning("Bad config data %s" % self.request.body)
            return

        firmware_file = '%s/version.py' % FIRMWARE_PATH
        if os.path.exists(firmware_file):
            with open(firmware_file, 'r') as infile:
                data = infile.read()
            version = int(data.split('=')[1])
            print('file version %s' % version)
            if version != device_config.get('version', None):
                self.write('{"upgrade": true}')
            else:
                self.write('{"upgrade": false}')

class DeviceHandler(BaseHandler):
    def put(self):
        print("some post")

    def get(self, path):
        print(path)
        with open('static/dino_control.html', 'r') as infile:
            self.write(infile.read())

    def post(self, path):
        global mqtt_client
        print(path)
        try:
            id, command = path.split('/')
            id = int(id)
            topic = '%d/dino_light' % id
            mqtt_client.publish(topic, command)
            print('publish %s to %s' % (command, topic))
        except Exception as e:
            print(e)
        print(self.request.body)

class ConfigHandler(BaseHandler):
    def put(self):
        print("some post")

    def get(self):
        self.write("Hello, world")

    def post(self):
        pass

basedir = os.path.abspath('')


application = MyApplication([
    (r"/config", ConfigHandler),
    (r"/update/(.*)", UpdateHandler),
    (r"/device/(.*)", DeviceHandler),
    (r"/", MyHandler),
    (r'/firmware/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(basedir, FIRMWARE_PATH)}),

])

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    client.subscribe("response")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


if __name__ == "__main__":
    global mqtt_client

    mqtt_user = os.environ.get('mqtt_user')
    mqtt_pw = os.environ.get('mqtt_pw')
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.username_pw_set(username=mqtt_user, password=mqtt_pw)
    mqtt_client.connect(MQTT_SERVER, 1883, 60)

    mqtt_client.loop_start()

    tornado.options.parse_command_line()
    signal.signal(signal.SIGINT, application.signal_handler)
    application.listen(8890)
    tornado.ioloop.PeriodicCallback(application.try_exit, 500).start()
    tornado.ioloop.IOLoop.instance().start()




