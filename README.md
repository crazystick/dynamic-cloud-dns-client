# Dynamic Cloud DNS Client

This is a simple client for the [Dynamic Cloud DNS](https://github.com/srueg/dynamic-cloud-dns) project.

Designed to run under Linux systemd, it consists of a small Python script, which uses the [ipify](https://www.ipify.org/) API to retrieve the current IP and if the IP address has changed, calls the cloud function configured as per the instructions for Dynamic Cloud DNS.

![](https://github.com/crazystick/dynamic-cloud-dns-client/workflows/Build/badge.svg)

## Prerequisites

Needs Python 3, requests and backoff

```
pip3 install -r requirements.txt
```

## Setup

 * Copy `dynamic_cloud_dns_client.py` to `/usr/local/bin`
 * Copy `dynamic-cloud-dns-client@.service` to `/etc/systemd/system`
 * Copy `dynamic_cloud_dns_client_your.host` to `/etc` (replace *your.host* with your actual hostname)
 * Edit `dynamic_cloud_dns_client_your.host` and fill in the environment variables
 * Enable and start your service: `systemctl enable dynamic_cloud_dns_client@your.host.service`

 Run `sudo ./install.sh your.host` to do the first 3 steps. Run just `sudo ./install.sh` to do the first two steps.

## Testing

Probably a good idea to do this in a virtualenv:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -t test-requirements.txt
pytest
```

## License

Copyright (c) 2020, Paul Adams. All rights reserved.

DCDNS Client is licensed under the MIT License.

See [LICENSE](LICENSE) for more details.
