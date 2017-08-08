
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/python
from flask import request, Request, jsonify
from flask import Flask
from flask import make_response
from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Consumer, Producer
import logging
import logging.handlers
import logging.config
import exampleservice_stats as stats
import threading
import subprocess
import six
import uuid
import datetime
from urlparse import urlparse
app = Flask(__name__)

start_publish = False
keystone_tenant_id='3a397e70f64e4e40b69b6266c634d9d0'
keystone_user_id='1e3ce043029547f1a61c1996d1a531a2'
rabbit_user='openstack'
rabbit_password='80608318c273f348a7c3'
rabbit_host='10.11.10.1'
rabbit_exchange='cord'
publisher_id='exampleservice_publisher'

@app.route('/monitoring/agent/exampleservice/start',methods=['POST'])
def exampleservice_start_monitoring_agent():
    global start_publish, rabbit_user, rabbit_password, rabbit_host, rabbit_exchange
    global keystone_tenant_id, keystone_user_id, publisher_id
    try:
        # To do validation of user inputs for all the functions
        target = request.json['target']
        logging.debug("target:%s",target)
        keystone_user_id = request.json['keystone_user_id']
        keystone_tenant_id = request.json['keystone_tenant_id']
        url = urlparse(target)
        rabbit_user = url.username
        rabbit_password = url.password
        rabbit_host = url.hostname

        setup_rabbit_mq_channel()

        start_publish = True
        periodic_publish()

        logging.info("Exampleservice monitoring is enabled")
        return "Exampleservice monitoring is enabled"
    except Exception as e:
            return e.__str__()

@app.route('/monitoring/agent/exampleservice/stop',methods=['POST'])
def openstack_stop():
    global start_publish
    start_publish = False
    logging.info ("Exampleservice monitoring is stopped")
    return "Exampleservice monitoring is stopped"


producer = None
def setup_rabbit_mq_channel():
     global producer
     global rabbit_user, rabbit_password, rabbit_host, rabbit_exchange,publisher_id
     service_exchange = Exchange(rabbit_exchange, "topic", durable=False)
     # connections/channels
     connection = BrokerConnection(rabbit_host, rabbit_user, rabbit_password)
     logging.info('Connection to RabbitMQ server successful')
     channel = connection.channel()
     # produce
     producer = Producer(channel, exchange=service_exchange, routing_key='notifications.info')
     p = subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE)
     (hostname, error) = p.communicate()
     publisher_id = publisher_id + '_on_' + hostname
     logging.info('publisher_id=%s',publisher_id)

def publish_exampleservice_stats(example_stats):
     global producer
     global keystone_tenant_id, keystone_user_id, publisher_id

     for k,v in example_stats.iteritems():
          msg = {'event_type': 'cord.'+k,
                 'message_id':six.text_type(uuid.uuid4()),
                 'publisher_id': publisher_id,
                 'timestamp':datetime.datetime.now().isoformat(),
                 'priority':'INFO',
                 'payload': {'counter_name':k,
                             'counter_unit':v['unit'],
                             'counter_volume':v['val'],
                             'counter_type':v['metric_type'],
                             'resource_id':'exampleservice',
                             'user_id':keystone_user_id,
                             'tenant_id':keystone_tenant_id
                            }
                }
          producer.publish(msg)
          logging.debug('Publishing exampleservice event: %s', msg)

def periodic_publish():
    global start_publish
    if not start_publish:
       return
    stats.retrieve_status_page()
    resParse = stats.parse_status_page()
    logging.debug ("publish:%(data)s" % {'data':resParse})
    publish_exampleservice_stats(resParse)
    threading.Timer(60, periodic_publish).start()

if __name__ == "__main__":
    logging.config.fileConfig('monitoring_agent.conf', disable_existing_loggers=False)
    logging.info ("Exampleservice monitoring is listening on port 5004")
    app.run(host="0.0.0.0",port=5004,debug=False)
