def __init__(self, *args, **kwargs):
    exampleservice = ExampleService.objects.all()
    if exampleservice:
        self._meta.get_field('provider_service').default = exampleservice[0].id
    super(ExampleTenant, self).__init__(*args, **kwargs)

def save(self, *args, **kwargs):
    super(ExampleTenant, self).save(*args, **kwargs)
    model_policy_exampletenant(self.pk)

def delete(self, *args, **kwargs):
    self.cleanup_container()
    super(ExampleTenant, self).delete(*args, **kwargs)

