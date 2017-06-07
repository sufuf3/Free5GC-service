from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.model_policies.model_policy_tenantwithcontainer import TenantWithContainerPolicy

class ExampleTenantPolicy(TenantWithContainerPolicy):
    model_name = "ExampleTenant"
