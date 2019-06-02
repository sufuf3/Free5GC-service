import base64
import jinja2
import json
import yaml
import os
import fileinput
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy
#from xossynchronizer.modelaccessor import *
#from xossynchronizer.model_policies.policy import Policy

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


class Free5GCServiceInstancePolicy(Policy):
    model_name = "Free5GCServiceInstance"

    def handle_create(self, service_instance):
        log.info("handle_create Free5GCServiceInstance")
        return self.handle_update(service_instance)

    def handle_update(self, service_instance):
        log.info("handle_update Free5GCServiceInstance", object=str(service_instance))
        t = TrustDomain(name="f5gc-trust", owner=KubernetesService.objects.first())
        t.save()
        owner = KubernetesService.objects.first()
        namespace = service_instance.namespace
        amf = service_instance.amf
        upf = service_instance.upf
        hss = service_instance.hss
        smf = service_instance.smf
        pcrf = service_instance.pcrf
        s1ap = service_instance.s1ap
        gtpu = service_instance.gtpu
        ## Configmaps
        cm_files = ["free5gc-cm.yaml", "freediameter-cm.yaml", "nextepc-cm.yaml"]
        for file in cm_files:
            input_file=os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), file)
            with open(input_file, 'r') as stream:
                try:
                    rd_tmp = json.dumps(yaml.load(stream), sort_keys=True, indent=2)
                    rd_tmp = rd_tmp.replace("MY_NAMESPACE", namespace)
                    rd_tmp = rd_tmp.replace("AMF_ADDR", amf)
                    rd_tmp = rd_tmp.replace("UPF_ADDR", upf)
                    rd_tmp = rd_tmp.replace("SMF_ADDR", smf)
                    rd_tmp = rd_tmp.replace("HSS_ADDR", hss)
                    rd_tmp = rd_tmp.replace("S1AP_ADDR", s1ap)
                    resource_definition = rd_tmp.replace("GTPU_ADDR", gtpu)
                    stream.close()
                except yaml.YAMLError as exc:
                    resource_definition="{}"
                    print(exc)
            name = "free5gc-cm-%s" % service_instance.id
            cm = KubernetesConfigMap(name=name, trust_domain=t,
                                              data=resource_definition)
            cm.save()
        ## AMF, SMF, UPF, HSS, PCRF
        yaml_files = ["amf-deploy.yaml", "hss-deploy.yaml", "pcrf-deploy.yaml", "smf-deploy.yaml", "upf-deploy.yaml"]
        for file in yaml_files:
            input_file=os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), file)
            with open(input_file, 'r') as stream:
                try:
                    rd_tmp = json.dumps(yaml.load(stream), sort_keys=True, indent=2)
                    rd_tmp = rd_tmp.replace("MY_NAMESPACE", '"vacio"')
                    rd_tmp = rd_tmp.replace("MY_NAMESPACE", namespace)
                    rd_tmp = rd_tmp.replace("AMF_ADDR", amf)
                    rd_tmp = rd_tmp.replace("UPF_ADDR", upf)
                    rd_tmp = rd_tmp.replace("SMF_ADDR", smf)
                    rd_tmp = rd_tmp.replace("HSS_ADDR", hss)
                    rd_tmp = rd_tmp.replace("S1AP_ADDR", s1ap)
                    resource_definition = rd_tmp.replace("GTPU_ADDR", gtpu)
                    stream.close()
                except yaml.YAMLError as exc:
                    resource_definition="{}"
                    print(exc)
            name = "free5gc-" + "%s" % service_instance.id
            instance = KubernetesResourceInstance(name=name, owner=owner,
                                              resource_definition=resource_definition,
                                              no_sync=False)
            instance.save()

      






    def handle_delete(self, service_instance):
        log.info("handle_delete Free5GCServiceInstance")
        service_instance.compute_instance.delete()
        service_instance.compute_instance = None
        service_instance.save(update_fields=["compute_instance"])
