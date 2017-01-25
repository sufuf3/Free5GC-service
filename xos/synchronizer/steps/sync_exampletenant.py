import os
import sys
from django.db.models import Q, F
from core.models import ModelLink, CoarseTenant, ServiceMonitoringAgentInfo
from services.exampleservice.models import ExampleService, ExampleTenant
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)

class SyncExampleTenant(SyncInstanceUsingAnsible):

    provides = [ExampleTenant]

    observes = ExampleTenant

    requested_interval = 0

    template_name = "exampletenant_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/exampleservice/exampleservice_private_key"

    watches = [ModelLink(CoarseTenant,via='coarsetenant'), ModelLink(ServiceMonitoringAgentInfo,via='monitoringagentinfo')]

    def __init__(self, *args, **kwargs):
        super(SyncExampleTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if (not deleted):
            objs = ExampleTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:
            # If this is a deletion we get all of the deleted tenants..
            objs = ExampleTenant.get_deleted_tenant_objects()

        return objs

    def get_exampleservice(self, o):
        if not o.provider_service:
            return None

        exampleservice = ExampleService.get_service_objects().filter(id=o.provider_service.id)

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

        objs = ExampleTenant.get_tenant_objects().all()
        for obj in objs:
            if obj.provider_service.id != monitoring_agent_info.service.id:
                logger.info("handle watch notifications for service monitoring agent info...ignoring because service attribute in monitoring agent info:%s is not matching" % (monitoring_agent_info))
                return

            instance = self.get_instance(obj)
            if not instance:
               logger.warn("handle watch notifications for service monitoring agent info...: No valid instance found for object %s" % (str(obj)))
               return

            logger.info("handling watch notification for monitoring agent info:%s for ExampleTenant object:%s" % (monitoring_agent_info, obj))

            #Run ansible playbook to update the routing table entries in the instance
            fields = self.get_ansible_fields(instance)
            fields["ansible_tag"] =  obj.__class__.__name__ + "_" + str(obj.id) + "_monitoring"
            fields["target_uri"] = monitoring_agent_info.target_uri

            template_name = "monitoring_agent.yaml"
            super(SyncExampleTenant, self).run_playbook(obj, fields, template_name)
        pass
