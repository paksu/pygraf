# Pytelegraf
> Python client for sending metrics to Telegraf inspired by pystatsd

[![Build Status](https://travis-ci.org/paksu/pytelegraf.svg?branch=master)](https://travis-ci.org/paksu/pytelegraf)

Designed to work with Telegraf UDP listener input plugin.
https://github.com/influxdata/telegraf/tree/master/plugins/inputs/udp_listener

Pytelegraf supports and is tested to function with Telegraf version **0.13** and newer. It may work with older versions too but that is untested.

Pytelegraf outputs InfluxDB line protocol https://docs.influxdata.com/influxdb/v0.13/write_protocols/line/

---
### Contacting
Need answers? Join pytelegraf on Gitter
[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/pytelegraf/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link)


If you find this library useful please let me know https://twitter.com/joonapaak

If you have an idea how this library can be improved then open an issue or even better send a pull request :)

### How to install
```pip install pytelegraf```

### Usage

```
from telegraf.client import TelegrafClient
client = TelegrafClient(host='localhost', port=8092)

# Records a single value with no tags
client.metric('some_metric', 123)

# Records a three values with different data types
client.metric('some_metric', {'value_a': 100, 'value_b': 100, 'value_c': True})

# Records a single value with one tag
client.metric('some_metric', 123, tags={'server_name': 'my-server'})
```

#### Global tags
The client can be initialized with global tags that will be sent with every metric implicitly

This is useful for adding tagging metrics by host or app
```
client = TelegrafClient(host='localhost', port=8092, tags={'host': 'my-host-001'})

# Records a single value
client.metric('some_metric', 123)
```

Because client was initialized with tags the metric contains them too so the line that was sent to Telegraf looks like this
```
some_metric,host=my-host-001 value=123i
```

Global tags can be overridden by defining them when sending a metric
```
# Records a single value with host tag
client.metric('some_metric', 123, tags={'host':'another-host-001', 'some_tag':'some_value'})
```

Will send the following line
```
some_metric,host=another-host-001,some_tag=some_value value=123i
```

### HTTP Client
The default `TelegrafClient` uses UDP to send metrics to Telegraf. The `HttpClient` works similarly, except that it issues requests via an HTTP POST. HTTP introduces non-trivial overhead, so to avoid blocking the main thread, these POSTs are issued in the background.

To use the `HttpClient`, `pytelegraf` must be installed like this: `pip install pytelegraf[http]`. Alternatively, add `pytelegraf[http]` to `requirements.txt`.

```
from telegraf import HttpClient

http_client = HttpClient(host='localhost', port=8186)
http_client.metric('some_metric', 123, tags={'server_name': 'my-server'})
```

### Telegraf configuration for versions 1.3 and higher
Just follow the sample configuration https://github.com/influxdata/telegraf/tree/master/plugins/inputs/socket_listener

```
[[inputs.socket_listener]]
  service_address = "udp://localhost:8092"
  data_format = "influx"
```

### Telegraf configuration for versions lower than 1.3
Just follow the sample configuration https://github.com/influxdata/telegraf/blob/b59266249dbeff43ba21bfd3dcc854b12eefd9ca/plugins/inputs/udp_listener/README.md

```
[[inputs.udp_listener]]
  service_address = "localhost:8092"
  allowed_pending_messages = 10000
  data_format = "influx"
```


### Using with Django

Define configuration in Django settings
```
TELEGRAF_HOST = 'localhost'
TELEGRAF_PORT = 8092
TELEGRAF_TAGS = {'some-global-tag': 'some-value'}
```

Then use the client in code
```
from telegraf.defaults.django import telegraf

telegraf.metric('some-metric', 1)
```

### How to develop

- Clone or fork this repo
- Make changes
- Install `tox` package
- Run tests with `tox`
- Submit a pull request

### Contributors
- bobo333
- sbi
- isvinogradov
- umax
