from service import XOSService
from services.exampleservice.models import ExampleService

class XOSExampleService(XOSService):
    provides = "tosca.nodes.ExampleService"
    xos_model = ExampleService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "private_key_fn", "versionNumber", "service_message"]


