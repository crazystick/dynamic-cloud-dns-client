import requests
from time import sleep
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

IPIFY4 = 'https://api.ipify.org?format=json'
IPIFY6 = 'https://api6.ipify.org?format=json'

def get_ipv4():
    r = requests.get(IPIFY4)
    r.raise_for_status()
    return r.json()['ip']

def get_ipv6():
    r = requests.get(IPIFY6)
    r.raise_for_status()
    return r.json()['ip']

def update_cloud_dns(ipv4=None, ipv6=None):
    if ipv4 is None and ipv6 is None:
        raise ValueError("No valid IP addresses given")

    data = {'token': os.environ['DCDNS_TOKEN'], 'host': os.environ['DCDNS_HOST']}

    if 'DCDNS_ZONE' in os.environ:
        data['zone'] = os.environ['DCDNS_ZONE']

    if ipv4 is not None:
        data['ipv4'] = ipv4

    if ipv6 is not None:
        data['ipv6'] = ipv6

    r = requests.post(os.environ['DCDNS_FUNCTION_URL'], data=data)

    r.raise_for_status()

    logger.info("IP addresses updated: IPv4={} IPv6={}".format(ipv4, ipv6))


if __name__ == "__main__":
    current_ipv4 = None
    current_ipv6 = None

    while True:
        if os.environ(['DCDNS_IPV4']) == 'YES':
            try:
                ipv4 = get_ipv4()
                if ipv4 == current_ipv4:
                    ipv4 = None
                else:
                    current_ipv4 = ipv4
            except requests.exceptions.HTTPError:
                ipv4 = None

        if os.environ(['DCDNS_IPV6']) == 'YES':
            try:
                ipv6 = get_ipv6()
                if ipv6 == current_ipv6:
                    ipv6 = None
                else:
                    current_ipv6 = ipv6
            except requests.exceptions.HTTPError:
                ipv6 = None

        try:
            update_cloud_dns(ipv4=ipv4, ipv6 = ipv6)
        except ValueError:
            logger.info("No IP address updates")
        except requests.exceptions.HTTPError as err:
            logger.exception(err)

        sleep(int(os.environ['DCDNS_FREQUENCY']))

