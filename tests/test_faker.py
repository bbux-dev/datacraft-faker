import datacraft
import pytest
from datacraft import SpecException


@pytest.mark.parametrize(
    "spec,locale,expected_key",
    [
        ({"name": {"type": "faker", "data": "name"}}, None, "name"),
        ({"address": {"type": "faker", "data": "address"}}, None, "address"),
        ({"email": {"type": "faker", "data": "email"}}, None, "email"),
        ({"name": {"type": "faker", "data": "name"}}, "fr_FR", "name"),
        ({"address": {"type": "faker", "data": "address"}}, "de_DE", "address"),
    ]
)
def test_faker_supplier(spec, locale, expected_key):
    if locale:
        spec[expected_key]["config"] = {"locale": locale}
    records = datacraft.entries(spec, 3)
    assert expected_key in records[0]
    for record in records:
        assert isinstance(record[expected_key], str)


def test_faker_supplier_with_provider():
    field_spec = {
        "type": "faker",
        "data": "vehicle_make_model",
        "config": {
            "providers": [
                {"faker_vehicle": "VehicleProvider"}
            ]
        }
    }
    models = datacraft.values_for(field_spec, 3)
    assert len(models) == 3


def test_invalid_spec():
    spec = {"name": {"type": "faker"}}
    with pytest.raises(SpecException):
        datacraft.entries(spec, 3)


def test_non_callable_method():
    spec = {"name": {"type": "faker", "data": "not_defined"}}
    with pytest.raises(ValueError):
        datacraft.entries(spec, 3)
