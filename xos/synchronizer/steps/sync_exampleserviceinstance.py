
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


import os
import sys
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)

class SyncExampleServiceInstance(SyncInstanceUsingAnsible):

    provides = [ExampleServiceInstance]

    observes = ExampleServiceInstance

    requested_interval = 0

    template_name = "exampleserviceinstance_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/exampleservice/exampleservice_private_key"

    watches = [ModelLink(ServiceDependency,via='servicedependency'), ModelLink(ServiceMonitoringAgentInfo,via='monitoringagentinfo')]

    def __init__(self, *args, **kwargs):
        super(SyncExampleServiceInstance, self).__init__(*args, **kwargs)

    def get_exampleservice(self, o):
        if not o.owner:
            return None

        exampleservice = ExampleService.objects.filter(id=o.owner.id)

        if not exampleservice:
            return None

        return exampleservice[0]

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        exampleservice = self.get_exampleservice(o)
        fields['service_message'] = exampleservice.service_message

        if o.foreground_color:
            fields["foreground_color"] = o.foreground_color.html_code

        if o.background_color:
            fields["background_color"] = o.background_color.html_code

        images=[]
        for image in o.embedded_images.all():
            images.append({"name": image.name,
                           "url": image.url})
        fields["images"] = images

        return fields

    def delete_record(self, port):
        # Nothing needs to be done to delete an exampleservice; it goes away
        # when the instance holding the exampleservice is deleted.
        pass

    def handle_service_monitoringagentinfo_watch_notification(self, monitoring_agent_info):
        if not monitoring_agent_info.service:
            logger.info("handle watch notifications for service monitoring agent info...ignoring because service attribute in monitoring agent info:%s is null" % (monitoring_agent_info))
            return

        if not monitoring_agent_info.target_uri:
            logger.info("handle watch notifications for service monitoring agent info...ignoring because target_uri attribute in monitoring agent info:%s is null" % (monitoring_agent_info))
            return

        objs = ExampleServiceInstance.objects.all()
        for obj in objs:
            if obj.owner.id != monitoring_agent_info.service.id:
                logger.info("handle watch notifications for service monitoring agent info...ignoring because service attribute in monitoring agent info:%s is not matching" % (monitoring_agent_info))
                return

            instance = self.get_instance(obj)
            if not instance:
               logger.warn("handle watch notifications for service monitoring agent info...: No valid instance found for object %s" % (str(obj)))
               return

            logger.info("handling watch notification for monitoring agent info:%s for ExampleServiceInstance object:%s" % (monitoring_agent_info, obj))

            #Run ansible playbook to update the routing table entries in the instance
            fields = self.get_ansible_fields(instance)
            fields["ansible_tag"] =  obj.__class__.__name__ + "_" + str(obj.id) + "_monitoring"
            fields["target_uri"] = monitoring_agent_info.target_uri

            template_name = "monitoring_agent.yaml"
            super(SyncExampleServiceInstance, self).run_playbook(obj, fields, template_name)
        pass
