# Dynamic Cloud DNS Client

This is a simple client for the [Dynamic Cloud DNS](https://github.com/srueg/dynamic-cloud-dns) project.

Designed to run under Linux systemd, it consists of a small Python script, which uses the [ipify](https://www.ipify.org/) API to retrieve the current IP and if the IP address has changed, calls the cloud function configured as per the instructions for Dynamic Cloud DNS.

# Setup

 * Copy `dynamic_cloud_dns_client.py` to `/usr/local/bin`
 * Copy `dynamic_cloud_dns_client@.service` to `/etc/systemd/system`
 * Copy `dynamic_cloud_dns_client_your.host` to `/etc` (replace *your.host* with your actual hostname)
 * Edit `dynamic_cloud_dns_client_your.host` and fill in the environment variables
 * Enable and start your service: `systemctl enable dynamic_cloud_dns_client@your.host.service`
