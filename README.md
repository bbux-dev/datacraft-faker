datacraft-faker
===============

Custom plugin for [datacraft](https://datacraft.readthedocs.io/en/latest) to wrap the [faker](https://faker.readthedocs.io/en/master/) python module

## Usage

The `datacraft-faker` module adds a `faker` Field Spec type to datacraft. This type allows a user to reference the
various data generation methods from faker in their Data Specs. For example:

```json
{
  "id": {"type":  "uuid"},
  "time:date.iso":  {},
  "name": {"type": "faker", "data": "name"},
  "dob:faker": "date_of_birth"
}
```

The above example uses two built in datacraft types `uuid` and `date.iso` and two faker ones. The record generated for
this spec will look something like:

```json
 {
  "id": "ad8f5737-59f9-48e3-bf4f-ed4deb357d0a",
  "time": "2024-07-18T19:57:17",
  "name": "Kimberly Wright",
  "dob": "1979-06-27"
}
```

The type for the field will always be `faker`. The `data` element of the spec is where you define the method name
that generates the data of interest. Here are a bunch of examples:


| Faker method         | 	Spec Example                                                  |
|----------------------|----------------------------------------------------------------|
| fake.name()          | 	{"name": {"type": "faker", "data": "name"}}                   |
| fake.address()       | 	{"address": {"type": "faker", "data": "address"}}             |
| fake.email()         | 	{"email": {"type": "faker", "data": "email"}}                 |
| fake.phone_number()  | 	{"phone_number": {"type": "faker", "data": "phone_number"}}   |
| fake.company()       | 	{"company": {"type": "faker", "data": "company"}}             |
| fake.date_of_birth() | 	{"date_of_birth": {"type": "faker", "data": "date_of_birth"}} |
| fake.text()          | 	{"text": {"type": "faker", "data": "text"}}                   |
| fake.city()          | 	{"city": {"type": "faker", "data": "city"}}                   |
| fake.state()         | 	{"state": {"type": "faker", "data": "state"}}                 |
| fake.zipcode()       | 	{"zipcode": {"type": "faker", "data": "zipcode"}}             |

Note that datacraft has a shorthand notation that works well for faker specs:

| Faker method         | Shorthand Spec                           |
|----------------------|------------------------------------------|
| fake.name()          | {"name:faker": "name"}                   |
| fake.address()       | {"address:faker": "address"}             |
| fake.email()         | {"email:faker": "email"}                 |
| fake.phone_number()  | {"phone_number:faker": "phone_number"}   |
| fake.company()       | {"company:faker": "company"}             |
| fake.date_of_birth() | {"date_of_birth:faker": "date_of_birth"} |
| fake.text()          | {"text:faker": "text"}                   |
| fake.city()          | {"city:faker": "city"}                   |
| fake.state()         | {"state:faker": "state"}                 |
| fake.zipcode()       | {"zipcode:faker": "zipcode"}             |


## Locales

Faker allows the ability to specify one or more locales to use for data generation. To configure this with a faker
Field Spec, add the config option `locale`:

```json
{
  "name": {
    "type": "faker",
    "data": "name",
    "config": {
      "locale": ["en_GB", "it_IT"]
    }
  },
  "email:faker?locale=en_GB,it_IT": "email"
}
```
The record generated for this spec will look something like:

```json
 {
  "name": "Anita Bosio",
  "email": "ocugia@example.net"
}
```

## Providers

To make use of other faker module providers, you will need to add the `include` config option:

```json
{
  "make_model": {
    "type": "faker",
    "data": "vehicle_make_model",
    "config": {
      "include": "faker_vehicle"
    }
  },
  "cat": {
    "type": "faker",
    "data": "vehicle_category",
    "config": {
      "include": "faker_vehicle"
    }
  },
  "year:faker?include=faker_vehicle": "vehicle_year"
}
```

The record generated for this spec will look something like:

```json
{
  "make_model": "Mercury Grand Marquis",
  "cat": "Hatchback",
  "year": "2014"
}
```

## Inspecting available faker types

Here is a shell command that can be used to list the available faker types

```bash
# assuming pip install faker already done
faker | grep '()' | sed 's/fake.\(.*\)()/\1/g' | awk '{print $1}'
```