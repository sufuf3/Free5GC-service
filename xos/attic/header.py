# models.py -  ExampleService Models

from core.models import Service, TenantWithContainer
from django.db import transaction
from django.db.models import *

SERVICE_NAME = 'exampleservice'
SERVICE_NAME_VERBOSE = 'Example Service'
SERVICE_NAME_VERBOSE_PLURAL = 'Example Services'
TENANT_NAME_VERBOSE = 'Example Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'Example Tenants'
