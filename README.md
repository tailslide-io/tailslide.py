<p align="center">
    <img src="https://user-images.githubusercontent.com/73451363/187207442-bae7ea26-7eac-4cab-8806-42779629c653.png" alt="Tailslide logo" width="400">
</p>

# Python SDK

---

This package is a server-side SDK for applications written in Python for the Tailslide feature flag framework.

Visit the https://github.com/tailslide-io repository or see Tailslide’s [case study](https://tailslide-io.github.io) page for more information.

## Installation

---

Install the Tailslide npm package with `pip install tailslide-sdk`

## Basic Usage

---

### Instantiating and Initializing FlagManager

The `FlagManager`class is the entry point of this SDK. It is responsible for retrieving all the flag rulesets for a given app with its `app_id` and creating new `Toggler` instances to handle toggling of feature flags within that app. To instantiate a `FlagManager` object, a user must provide a configuration object:

```python
import asyncio
from tailslide import FlagManager

config = {
    "nats_server": "nats://localhost:4222",
    "nats_stream": "flags_ruleset",
    "app_id": 1,
    "user_context": "375d39e6-9c3f-4f58-80bd-e5960b710295",
    "sdk_key": "myToken",
    "redis_host": "http://localhost",
    "redis_port": 6379,
}

async def main():
    manager = FlagManager(**config)
    await manager.initialize()

asyncio.run(main())
```

- `nats_server` is the NATS JetStream server `address:port`
- `nats_stream` is the NATS JetStream’s stream name that stores all the apps and their flag rulesets
- `app_id` is the ID number of the app the user wants to retrieve its flag ruleset from
- `user_context` is the UUID string that identifies the current user
- `sdk_key` is the SDK key for the Tailslide, it is used as a password for NATS JetStream token authentication
- `redis_host` is the address to the Redis database
- `redis_port` is the port number that the Redis database runs on

After instantiating a `FlagManager`, invoke the `initialize` method. This method connects the `FlagManager` instance to both NATS JetStream and Redis Timeseries, and asynchronously retrieves the latest and any new flag ruleset data.

---

### Using Feature Flag with Toggler

Once the `FlagManager` is initialized, it can create a `Toggler`, with the `new_toggler` method, for each feature flag that the developer wants to wrap the new and old features in. A `Toggler`’s `is_flag_active` method checks whether the flag with its `flag_name` is active or not based on the flag ruleset. A `Toggler`’s `is_flag_active` method returns a boolean value, which can be used to evaluate whether a new feature should be used or not.

```python
flag_config = {
    "flag_name": 'App 1 Flag 1',
}

flag_toggler = manager.new_toggler(flag_config)

if flag_toggler.is_flag_active():
    # call new feature here
else:
    # call old feature here
```

---

### Emitting Success or Failture

To use a `Toggler` instance to record successful or failed operations, call its `emit_success` or `emit_failure` methods:

```python
if successCondition:
    flag_toggler.emit_success()
else:
    flag_toggler.emit_failure()
```

## Documentation

---

### FlagManager

The `FlagManager` class is the entry point of the SDK. A new `FlagManager` object will need to be created for each app.

#### FlagManager Constructor

**Parameters:**

- An object with the following keys
  - `nats_server` is the NATS JetStream server `address:port`
  - `nats_stream` is the NATS JetStream’s stream name that stores all the apps and their flag rulesets
  - `app_id` a number representing the application the microservice belongs to
  - `sdk_key` a string generated via the Tower front-end for NATS JetStream authentication
  - `user_context` a string representing the user’s UUID
  - `redis_host` a string that represents the url of the Redis server
  - `redis_port` a number that represents the port number of the Redis server

---

#### Instance Methods

##### `flagmanager.initialize()`

Asynchronously initialize `flagmanager` connections to NATS JetStream and Redis database

**Parameters:**

- `None`

**Return Value:**

- `None`

---

##### `flagmanager.set_user_context(new_user_context)`

Set the current user's context for the `flagmanager`

**Parameters:**

- `new_user_context`: A UUID string that represents the current active user

**Return Value:**

- `None`

---

##### `flagmanager.get_user_context()`

Returns the current user context

**Parameters:**

- `None`

**Return Value:**

- The UUID string that represents the current active user

---

##### `flagmanager.new_toggler(options)`

Creates a new toggler to check for a feature flag's status from the current app's flag ruleset by the flag's name.

**Parameters:**

- `options`: An object with key of `flag_name` and a string value representing the name of the feature flag for the new toggler to check whether the new feature is enabled

**Return Value:**

- A `Toggler` object

---

##### `flagmanager.disconnect()`

Asynchronously disconnects the `FlagManager` instance from NATS JetStream and Redis database

**Parameters:**

- `None`

**Return Value:**

- `None`

---

### Toggler

The Toggler class provides methods that determine whether or not new feature code is run and handles success/failure emissions. Each toggler handles one feature flag, and is created by `flagmanager.new_toggler()`.

---

#### Instance Methods

##### `toggler.is_flag_active()`

Checks for flag status, whitelisted users, and rollout percentage in that order to determine whether the new feature is enabled.

- If the flag's active status is false, the function returns `False`
- If current user's UUID is in the whitelist of users, the function returns `True`
- If current user's UUID hashes to a value within user rollout percentage, the function returns `True`
- If current user's UUID hashes to a value outside user rollout percentage, the function returns `False`

**Parameters:**

- `None`

**Return Value**

- `True` or `False` depending on whether the feature flag is active

---

##### `toggler.emit_success()`

Records a successful operation to the Redis Timeseries database, with key `flagId:success` and value of current timestamp

**Parameters:**

- `None`

**Return Value**

- `None`

---

##### `toggler.emit_failure()`

Records a failure operation to the Redis Timeseries database, with key `flagId:success` and value of current timestamp

**Parameters:**

- `None`

**Return Value**

- `None`
