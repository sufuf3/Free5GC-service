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

from xosresource import XOSResource
from core.models import Service
from services.exampleservice.models import ExampleServiceInstance

class XOSExampleServiceInstance(XOSResource):
    provides = ["tosca.nodes.ExampleServiceInstance",
                "tosca.nodes.ExampleTenant"            # deprecated
                ]
    xos_model = ExampleServiceInstance
    name_field = "service_specific_id"
    copyin_props = ("tenant_message",)

    def get_xos_args(self, throw_exception=True):
        args = super(XOSExampleServiceInstance, self).get_xos_args()

        # ExampleServiceInstance must always have a provider_service
        provider_name = self.get_requirement("tosca.relationships.TenantOfService", throw_exception=True)
        if provider_name:
            args["owner"] = self.get_xos_object(Service, throw_exception=True, name=provider_name)

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        return ExampleServiceInstance.objects.filter(owner=args["owner"], service_specific_id=args["service_specific_id"])
        return []

    def can_delete(self, obj):
        return super(XOSExampleServiceInstance, self).can_delete(obj)

