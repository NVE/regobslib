# regobslib — A Regobs client library

This client library aim to simplify interaction with the Regobs API v5.

## Prerequisites

* A client ID for the test or prod environment, contact [regobs@nve.no](mailto:regobs@nve.no) to acquire this.
* A user account for the test or prod environment. Register here:
  * Test environment: [https://test-konto.nve.no/](https://test-konto.nve.no/)
  * Prod environment: [https://konto.nve.no/](https://konto.nve.no/)
* Basic knowledge about snow science nomenclature. For more info, see the following resources:
  * [NVE Field Book](https://www.varsom.no/media/2265/nve-forsvaret_feltha-ndbok_innmat_v1.pdf)
  * [Observation Guidelines and Recording Standards for Weather, Snowpack and Avalanches](https://www.avalancheassociation.ca/resource/resmgr/standards_docs/ogrs2016web.pdf)
  * [Snow, Weather and Avalanches](https://static1.squarespace.com/static/59d2a0f0e9bfdf20d6d654b7/t/5a1af2a5652dea2e1a5ea055/1511715529879/AAA_SWAG_Web+2.pdf)

## Installation

To install using `pip`:
```
pip install regobslib
```

## Example programs

### Searching for data

Here is an example program searching for weather observations in Ofoten.

```python
from regobslib import *

connection = Connection(prod=True)
results = connection.search(SnowRegistration, regions=[SnowRegion.OFOTEN], observation_types=[Weather])

print(f"Length of results: {len(results)}\n")

print("First result")
print(results[0])

print("\nIterates over results")
for result in results:
    print(f"Id: {result.id}, Observer: {result.observer.nickname}, Date: {result.obs_time}")
```

### Submitting data

Below is a simple program demonstrating how to register a whumpf sound
at a given location and time.

```python
from regobslib import *
import datetime as dt

# Contact regobs@nve.no to get a client ID.
CLIENT_ID = "00000000-0000-0000-0000-000000000000"

# Create a user at https://test-konto.nve.no/ or https://konto.nve.no/
USERNAME = "ola.nordmann@example.com"
PASSWORD = "P4ssw0rd"

# First we create an empty SnowRegistration object
reg = SnowRegistration(REGOBS_TZ.localize(dt.datetime(2021, 8, 17, 9, 48)),
                       Position(lat=68.4293, lon=18.2572))

# Then we add a DangerSign observation to it
reg.add_danger_sign(DangerSign(DangerSign.Sign.WHUMPF_SOUND))

# Authenticate to Regobs to be able to submit observations
connection = Connection(prod=False).authenticate(USERNAME, PASSWORD, CLIENT_ID)

# Send our SnowRegistration to Regobs
stored_reg = connection.submit(reg)
print(stored_reg)
```

For a more extensive demonstration, refer to [demo.py](https://github.com/NVE/regobslib/blob/master/demo.py).

## Documentation

We have yet to write documentation, but the function declarations
are written with type hints and most parameters are enums, so the code in
[submit.py](https://github.com/NVE/regobslib/blob/master/src/regobslib/submit.py) may help you on your way. A properly set
up IDE will also use the type hints and enums to inform you about your
alternatives.

You can also use GitHubs built-in code navigation to quickly find the
definition of a class or method in the [example code](https://github.com/NVE/regobslib/blob/master/demo.py).
