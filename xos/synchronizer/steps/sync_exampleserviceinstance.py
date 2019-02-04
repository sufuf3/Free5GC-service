
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
import time
from xossynchronizer.steps.syncstep import SyncStep, DeferredException
from xossynchronizer.ansible_helper import run_template_ssh
from xossynchronizer.modelaccessor import ExampleServiceInstance
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

# TODO(smbaker): Move this to the core
class SyncServiceInstanceWithComputeUsingAnsible(SyncStep):
    def __init__(self, *args, **kwargs):
        SyncStep.__init__(self, *args, **kwargs)

    def defer_sync(self, o, reason):
        log.info("defer object", object = str(o), reason = reason, **o.tologdict())
        raise DeferredException("defer object %s due to %s" % (str(o), reason))

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes that aren't part of the
        # object itself.

        return {}

    def run_playbook(self, o, fields, template_name=None):
        if not template_name:
            template_name = self.template_name
        tStart = time.time()
        run_template_ssh(template_name, fields, object=o)
        log.info("playbook execution time", time=int(time.time() - tStart), **o.tologdict())

    def get_ssh_ip(self, instance):
        for port in instance.ports.all():
            if port.network.template and port.network.template.vtn_kind == "MANAGEMENT_LOCAL":
                return port.ip

        for port in instance.ports.all():
            if port.network.template and port.network.template.vtn_kind == "MANAGEMENT_HOST":
                return port.ip

        return None

    def get_ansible_fields(self, instance):
        # return all of the fields that tell Ansible how to talk to the context
        # that's setting up the container.

        # Cast to the leaf_model. For OpenStackServiceInstance, this will allow us access to fields like "node"
        instance = instance.leaf_model

        node = getattr(instance, "node")
        if not node:
            raise Exception("Instance has no node for instance %s" % str(instance))

        if not instance.slice:
            raise Exception("Instance has no slice for instance %s" % str(instance))

        if not instance.slice.service:
            raise Exception("Instance's slice has no service for instance %s" % str(instance))

        if not instance.slice.service.private_key_fn:
            raise Exception("Instance's slice's service has no private_key_fn for instance %s" % str(instance))

        key_name = instance.slice.service.private_key_fn
        if not os.path.exists(key_name):
            raise Exception("Node key %s does not exist for instance %s" % (key_name, str(instance)))

        ssh_ip = self.get_ssh_ip(instance)
        if not ssh_ip:
            raise Exception("Unable to determine ssh ip for instance %s" % str(instance))

        key = file(key_name).read()

        fields = {"instance_name": instance.name,
                  "hostname": node.name,
                  "username": "ubuntu",
                  "ssh_ip": ssh_ip,
                  "private_key": key,
                  "instance_id": "none", # is not used for proxy-ssh ansible connections
                  }

        return fields

    def sync_record(self, o):
        log.info("sync'ing object", object=str(o), **o.tologdict())

        compute_service_instance = o.compute_instance
        if not compute_service_instance:
            self.defer_sync(o, "waiting on instance")
            return

        if not compute_service_instance.backend_handle:
            self.defer_sync(o, "waiting on instance.backend_handle")
            return

        fields = self.get_ansible_fields(compute_service_instance)

        fields["ansible_tag"] = getattr(o, "ansible_tag", o.__class__.__name__ + "_" + str(o.id))

        fields.update(self.get_extra_attributes(o))

        self.run_playbook(o, fields)

        o.save()

class SyncExampleServiceInstance(SyncServiceInstanceWithComputeUsingAnsible):

    provides = [ExampleServiceInstance]

    observes = ExampleServiceInstance

    requested_interval = 0

    template_name = "exampleserviceinstance_playbook.yaml"

    def __init__(self, *args, **kwargs):
        super(SyncExampleServiceInstance, self).__init__(*args, **kwargs)

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        exampleservice = o.owner.leaf_model
        fields['service_message'] = exampleservice.service_message

        if o.foreground_color:
            fields["foreground_color"] = o.foreground_color.html_code

        if o.background_color:
            fields["background_color"] = o.background_color.html_code

        images = []
        for image in o.embedded_images.all():
            images.append({"name": image.name,
                           "url": image.url})
        fields["images"] = images

        return fields

    def delete_record(self, port):
        # Nothing needs to be done to delete an exampleservice; it goes away
        # when the instance holding the exampleservice is deleted.
        pass

