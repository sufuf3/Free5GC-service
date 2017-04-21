def model_policy_exampletenant(pk):
    with transaction.atomic():
        tenant = ExampleTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()

