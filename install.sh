#!/bin/sh

[ -f dynamic_cloud_dns_client.py ] || exit
cp dynamic_cloud_dns_client.py /usr/local/bin/dynamic_cloud_dns_client.py
cp dynamic-cloud-dns-client@.service /etc/systemd/system

if [ -n "$1" ]; then
  cp dynamic_cloud_dns_client_your.host "/etc/dynamic_cloud_dns_client_$1"
  echo "Edit /etc/dynamic_cloud_dns_client_$1 and then run systemctl enable dynamic_cloud_dns_client@$1.service"
fi
