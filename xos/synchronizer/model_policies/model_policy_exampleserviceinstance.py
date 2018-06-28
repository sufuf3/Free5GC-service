
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


from synchronizers.new_base.modelaccessor import OpenStackService, Service
from synchronizers.new_base.policy import Policy
from synchronizers.new_base.model_policies.model_policy_tenantwithcontainer import LeastLoadedNodeScheduler

class ExampleServiceInstancePolicy(Policy):
    model_name = "ExampleServiceInstance"

    def handle_create(self, service_instance):
        return self.handle_update(service_instance)

    def handle_update(self, service_instance):
        if not service_instance.compute_instance:
            # TODO: Break dependency
            compute_service = OpenStackService.objects.first()
            compute_service_instance_class = Service.objects.get(id=compute_service.id).get_service_instance_class()

            exampleservice = service_instance.owner.leaf_model

            # TODO: What if there is the wrong number of slices?
            slice = exampleservice.slices.first()

            # TODO: What if there is no default image?
            image = slice.default_image

            # TODO: What if there is no default flavor?
            flavor = slice.default_flavor

            if slice.default_node:
                node = slice.default_node
            else:
                scheduler = LeastLoadedNodeScheduler
                # TODO(smbaker): Labeling and constraints
                (node, parent) = scheduler(slice).pick()

            name="exampleserviceinstance-%s" % service_instance.id
            compute_service_instance = compute_service_instance_class(slice=slice,
                                                                      owner=compute_service,
                                                                      image=image,
                                                                      flavor=flavor,
                                                                      name=name,
                                                                      node=node)
            compute_service_instance.save()

            service_instance.compute_instance = compute_service_instance
            service_instance.save(update_fields=["compute_instance"])

    def handle_delete(self, service_instance):
        if service_instance.compute_instance:
            service_instance.compute_instance.delete()
            service_instance.compute_instance = None
            # TODO: I'm not sure we can save things that are being deleted...
            service_instance.save(update_fields=["compute_instance"])

