from header import *



#from core.models.service import Service
from core.models import Service



#from core.models.tenantwithcontainer import TenantWithContainer
from core.models import TenantWithContainer





class ExampleService(Service):

  KIND = "exampleservice"

  class Meta:
      app_label = "exampleservice"
      name = "exampleservice"
      verbose_name = "Example Service"

  # Primitive Fields (Not Relations)
  service_message = CharField( help_text = "Service Message to Display", max_length = 254, null = False, db_index = False, blank = False )
  

  # Relations
  

  
  pass




class ExampleTenant(TenantWithContainer):

  KIND = "exampleservice"

  class Meta:
      app_label = "exampleservice"
      name = "exampletenant"
      verbose_name = "Example Tenant"

  # Primitive Fields (Not Relations)
  tenant_message = CharField( help_text = "Tenant Message to Display", max_length = 254, null = False, db_index = False, blank = False )
  

  # Relations
  

  def __init__(self, *args, **kwargs):
      exampleservice = ExampleService.get_service_objects().all()
      if exampleservice:
          self._meta.get_field('provider_service').default = exampleservice[0].id
      super(ExampleTenant, self).__init__(*args, **kwargs)
  
  def save(self, *args, **kwargs):
      super(ExampleTenant, self).save(*args, **kwargs)
      model_policy_exampletenant(self.pk)
  
  def delete(self, *args, **kwargs):
      self.cleanup_container()
      super(ExampleTenant, self).delete(*args, **kwargs)
  
  pass

def model_policy_exampletenant(pk):
    with transaction.atomic():
        tenant = ExampleTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()


