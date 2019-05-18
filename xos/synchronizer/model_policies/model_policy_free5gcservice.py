
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

import base64
import jinja2
import json
import yaml
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


class Free5GCServicePolicy(Policy):
    model_name = "Free5GCService"

    def handle_create(self, service_instance):
        log.info("[Handle] Create Free5GCService")
        return self.handle_update(service_instance)

    def handle_update(self, service_instance):
        log.info("[Handle] Update Free5GCService")
        name = "free5gc-%s" % service_instance.id
        log.info(self)
        log.info(service_instance)
        log.info(KubernetesService.objects.first())
        compute_service_instance = Free5GCServiceInstance(name=name, owner=service_instance,
                                                            no_sync=False)
        compute_service_instance.save()

    def handle_delete(self, service_instance):
        log.info("[Handle] Delete Free5GCService")
        service_instance.compute_instance.delete()
        service_instance.compute_instance = None
        service_instance.save(update_fields=["compute_instance"])
