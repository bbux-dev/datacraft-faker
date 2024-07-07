import importlib
import json
import logging
from typing import Callable

import datacraft
import datacraft._registered_types.common as common
from datacraft import ValueSupplierInterface, SpecException
from faker import Faker

_FAKER_KEY = "faker"
_log = logging.getLogger(__name__)


####################
# Schema Definitions
####################


@datacraft.registry.schemas(_FAKER_KEY)
def _schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://github.com/bbux-dev/datacraft-faker/schemas/faker.schema.json",
        "type": "object",
        "properties": {
            "type": {"type": "string", "pattern": f"^faker$"},
            "data": {"type": "string"},
            "config": {
                "type": "object",
                "properties": {
                    "locale": {
                        "type": "string"
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
        return self.fake_func()

# Example usage:
# provider = _dynamic_import('faker_vehicle', 'VehicleProvider')
def _dynamic_import(module_name, class_name):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


@datacraft.registry.types(_FAKER_KEY)
def _supplier(field_spec, loader: datacraft.Loader):
    """ configure the supplier for mgrs types """
    if "data" not in field_spec or not (isinstance(field_spec["data"], str)):
        raise SpecException(f"data field as string is required for faker spec: {json.dumps(field_spec)}")
    config = datacraft.utils.load_config(field_spec, loader)
    fake = Faker(config.get("locale", "en_US"))
    if "providers" in config:
        providers = config["providers"]
        if not (isinstance(providers, list)) or not all(isinstance(entry, dict) for entry in providers):
            raise SpecException(
                "providers config must be list of dictionaries representing module to class to import as provider")
        for entry in providers:
            for module_name, class_name in entry.items():
                # Dynamic import and add provider to faker instance
                imported_class = _dynamic_import(module_name, class_name)
                fake.add_provider(imported_class)

    faker_function = _get_faker_method(fake, field_spec["data"])
    return FakerSupplier(faker_function)


def _get_faker_method(faker, method_path) -> Callable:
    parts = method_path.split('.')
    obj = faker
    for part in parts:
        if hasattr(obj, part):
            obj = getattr(obj, part)
        else:
            raise ValueError(f"Faker method {method_path} does not exist")

    if callable(obj):
        return obj
    else:
        raise ValueError(f"{method_path} is not a callable method")


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
        }
    }
    return common.standard_example_usage(example, 3)


def load_custom():
    """ called by datacraft entrypoint loader """
    pass
