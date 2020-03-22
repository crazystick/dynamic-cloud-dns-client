import pytest
from urllib.parse import parse_qs

from dynamic_cloud_dns_client import *


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("DCDNS_IPV4", "YES")
    monkeypatch.setenv("DCDNS_IPV6", "YES")
    monkeypatch.setenv("DCDNS_TOKEN", "TEST_TOKEN")
    monkeypatch.setenv("DCDNS_HOST", "TEST_HOST")
    monkeypatch.setenv("DCDNS_ZONE", "TEST_ZONE")
    monkeypatch.setenv("DCDNS_FUNCTION_URL", "https://cloudfunctions.net.mock/updateHost")

def test_get_ipv4(requests_mock):
    # given
    requests_mock.get(IPIFY4, json={'ip': '0.0.0.0'})

    # when
    ip = get_ipv4()

    # then
    assert ip == '0.0.0.0'

def test_get_ipv6(requests_mock):
    # given
    requests_mock.get(IPIFY6, json={'ip': '2001:0db8:0000:0000:0000:8a2e:0370:7334'})

    # when
    ip = get_ipv6()

    # then
    assert ip == '2001:0db8:0000:0000:0000:8a2e:0370:7334'

def test_update_cloud_dns_both(env_vars, requests_mock):
    # given
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")
    ipv4 = '0.0.0.0'
    ipv6 = '2001:0db8:0000:0000:0000:8a2e:0370:7334'

    # when
    update_cloud_dns(ipv4, ipv6)

    # then
    assert requests_mock.called
    assert requests_mock.call_count == 1
    posted_data = parse_qs(requests_mock.request_history[0].text)
    assert posted_data['ipv4'][0] == ipv4
    assert posted_data['ipv6'][0] == ipv6

def test_update_cloud_dns_ipv4(env_vars, requests_mock):
    # given
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")
    ipv4 = '0.0.0.0'
    ipv6 = None

    # when
    update_cloud_dns(ipv4, ipv6)

    # then
    assert requests_mock.called
    assert requests_mock.call_count == 1
    posted_data = parse_qs(requests_mock.request_history[0].text)
    assert posted_data['ipv4'][0] == ipv4
    assert 'ipv6' not in posted_data

def test_update_cloud_dns_ipv6(env_vars, requests_mock):
    # given
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")
    ipv4 = None
    ipv6 = '2001:0db8:0000:0000:0000:8a2e:0370:7334'

    # when
    update_cloud_dns(ipv4, ipv6)

    # then
    assert requests_mock.called
    assert requests_mock.call_count == 1
    posted_data = parse_qs(requests_mock.request_history[0].text)
    assert 'ipv4' not in posted_data
    assert posted_data['ipv6'][0] == ipv6

def test_update_cloud_dns_none(env_vars, requests_mock):
    # given
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")
    ipv4 = None
    ipv6 = None

    # when
    with pytest.raises(ValueError):
        update_cloud_dns(ipv4, ipv6)

    # then
    assert not requests_mock.called
    assert requests_mock.call_count == 0

def test_main_no_update(env_vars, requests_mock):
    # given
    requests_mock.get(IPIFY4, json={'ip': '0.0.0.0'})
    requests_mock.get(IPIFY6, json={'ip': '2001:0db8:0000:0000:0000:8a2e:0370:7334'})
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")

    # when
    ipv4, ipv6 = do_update('0.0.0.0', '2001:0db8:0000:0000:0000:8a2e:0370:7334')

    # then
    assert ipv4 == '0.0.0.0'
    assert ipv6 == '2001:0db8:0000:0000:0000:8a2e:0370:7334'
    assert requests_mock.call_count == 2
    assert requests_mock.request_history[0].url == IPIFY4
    assert requests_mock.request_history[1].url == IPIFY6

def test_main_does_update(env_vars, requests_mock):
    # given
    requests_mock.get(IPIFY4, json={'ip': '1.2.3.4'})
    requests_mock.get(IPIFY6, json={'ip': '2001:0db8:9999:0000:0000:8a2e:0370:7334'})
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")

    # when
    ipv4, ipv6 = do_update('0.0.0.0', '2001:0db8:0000:0000:0000:8a2e:0370:7334')

    # then
    assert ipv4 == '1.2.3.4'
    assert ipv6 == '2001:0db8:9999:0000:0000:8a2e:0370:7334'
    assert requests_mock.call_count == 3
    assert requests_mock.request_history[0].url == IPIFY4
    assert requests_mock.request_history[1].url == IPIFY6
    assert requests_mock.request_history[2].url == "https://cloudfunctions.net.mock/updateHost"

def test_main_single_retry(env_vars, requests_mock):
    # given
    requests_mock.get(IPIFY4, [{'exc': requests.exceptions.ConnectTimeout},{'json': {'ip': '1.2.3.4'}}])
    requests_mock.get(IPIFY6, json={'ip': '2001:0db8:9999:0000:0000:8a2e:0370:7334'})
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")

    # when
    ipv4, ipv6 = do_update('0.0.0.0', '2001:0db8:0000:0000:0000:8a2e:0370:7334')

    # then
    assert ipv4 == '1.2.3.4'
    assert ipv6 == '2001:0db8:9999:0000:0000:8a2e:0370:7334'
    assert requests_mock.call_count == 4
    assert requests_mock.request_history[0].url == IPIFY4
    assert requests_mock.request_history[1].url == IPIFY4
    assert requests_mock.request_history[2].url == IPIFY6
    assert requests_mock.request_history[3].url == "https://cloudfunctions.net.mock/updateHost"

def test_main_max_retry(env_vars, requests_mock):
    # given
    requests_mock.get(IPIFY4, [
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout}])
    requests_mock.get(IPIFY6, [
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout},
        {'exc': requests.exceptions.ConnectTimeout}])
    requests_mock.post("https://cloudfunctions.net.mock/updateHost")

    # when
    ipv4, ipv6 = do_update('0.0.0.0', '2001:0db8:0000:0000:0000:8a2e:0370:7334')

    # then
    assert ipv4 == '0.0.0.0'
    assert ipv6 == '2001:0db8:0000:0000:0000:8a2e:0370:7334'
    assert requests_mock.call_count == 10
    assert requests_mock.request_history[0].url == IPIFY4
    assert requests_mock.request_history[1].url == IPIFY4
    assert requests_mock.request_history[2].url == IPIFY4
    assert requests_mock.request_history[3].url == IPIFY4
    assert requests_mock.request_history[4].url == IPIFY4
    assert requests_mock.request_history[5].url == IPIFY6
    assert requests_mock.request_history[6].url == IPIFY6
    assert requests_mock.request_history[7].url == IPIFY6
    assert requests_mock.request_history[8].url == IPIFY6
    assert requests_mock.request_history[9].url == IPIFY6
