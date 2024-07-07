import importlib
import inspect
import json
import logging
from typing import Callable

import datacraft
import datacraft._registered_types.common as common
from datacraft import ValueSupplierInterface, SpecException
from faker import Faker
from faker.providers import BaseProvider

_FAKER_KEY = "faker"
_log = logging.getLogger(__name__)


####################
# Schema Definitions
####################
@datacraft.registry.schemas(_FAKER_KEY)
def _schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://github.com/bbux-dev/datacraft-faker/schemas/faker.schema.json",
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": "^faker$"
            },
            "data": {
                "type": "string"
            },
            "config": {
                "type": "object",
                "properties": {
                    "locale": {
                        "oneOf": [
                            {
                                "type": "string"
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        ]
                    },
                    "include": {
                        "oneOf": [
                            {
                                "type": "string"
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        ]
                    }
                }
            }
        }
    }


####################
# Type Definitions
####################
class FakerSupplier(ValueSupplierInterface):
    def __init__(self, fake_func: str):
        self.fake_func = fake_func

    def next(self, iteration):
        return str(self.fake_func())


# Example usage:
# provider = _dynamic_import('faker_vehicle')
def _dynamic_import(module_name):
    module = importlib.import_module(module_name)
    return module


@datacraft.registry.types(_FAKER_KEY)
def _supplier(field_spec, loader: datacraft.Loader):
    """ configure the supplier for mgrs types """
    if "data" not in field_spec or not (isinstance(field_spec["data"], str)):
        raise SpecException(f"data field as string is required for faker spec: {json.dumps(field_spec)}")
    config = datacraft.utils.load_config(field_spec, loader)
    locale = config.get("locale", "en_US")
    if isinstance(locale, str):
        locale = locale.split(";") if ";" in locale else locale.split(",")
    fake = Faker(locale)
    if "include" in config:
        _load_providers(config, fake)

    faker_function = _get_faker_method(fake, field_spec["data"])
    return FakerSupplier(faker_function)


def _load_providers(config, fake):
    providers = config.get("include", [])
    if isinstance(providers, str):
        providers = providers.split(";") if ";" in providers else providers.split(",")
    if not isinstance(providers, list) or not all(isinstance(entry, str) for entry in providers):
        raise SpecException("include config must be a single or list of module names to import as provider")

    for module_name in providers:
        module = _dynamic_import(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseProvider) and obj is not BaseProvider:
                fake.add_provider(obj)


def _get_faker_method(faker, method_path) -> Callable:
    parts = method_path.split('.')
    obj = faker
    for part in parts:
        if hasattr(obj, part):
            obj = getattr(obj, part)
        else:
            raise SpecException(f"Faker method {method_path} does not exist")

    if callable(obj):
        return obj
    else:
        raise SpecException(f"{method_path} is not a callable method")


###########################
# Usage Definitions
###########################
@datacraft.registry.usage(_FAKER_KEY)
def _usage():
    """ configure the usage for mgrs types """
    example = {
        "name": {
            "type": "faker",
            "data": "name",
            "config": {
                "locale": "fr_FR"
            }
        },
        "vehicle": {
            "type": "faker",
            "data": "vehicle_make_model",
            "config": {
                "include": "faker_vehicle"
            }
        }
    }
    return common.standard_example_usage(example, 3)


def load_custom():
    """ called by datacraft entrypoint loader """
    pass
