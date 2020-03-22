
from dynamic_cloud_dns_client import *

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

def test_main_no_update(requests_mock, monkeypatch):
	# given
	monkeypatch.setenv("DCDNS_IPV4", "YES")
	monkeypatch.setenv("DCDNS_IPV6", "YES")
	monkeypatch.setenv("DCDNS_TOKEN", "TEST_TOKEN")
	monkeypatch.setenv("DCDNS_HOST", "TEST_HOST")
	monkeypatch.setenv("DCDNS_ZONE", "TEST_ZONE")
	monkeypatch.setenv("DCDNS_FUNCTION_URL", "https://cloudfunctions.net.mock/updateHost")
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

def test_main_does_update(requests_mock, monkeypatch):
	# given
	monkeypatch.setenv("DCDNS_IPV4", "YES")
	monkeypatch.setenv("DCDNS_IPV6", "YES")
	monkeypatch.setenv("DCDNS_TOKEN", "TEST_TOKEN")
	monkeypatch.setenv("DCDNS_HOST", "TEST_HOST")
	monkeypatch.setenv("DCDNS_ZONE", "TEST_ZONE")
	monkeypatch.setenv("DCDNS_FUNCTION_URL", "https://cloudfunctions.net.mock/updateHost")
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

def test_main_single_retry(requests_mock, monkeypatch):
	# given
	monkeypatch.setenv("DCDNS_IPV4", "YES")
	monkeypatch.setenv("DCDNS_IPV6", "YES")
	monkeypatch.setenv("DCDNS_TOKEN", "TEST_TOKEN")
	monkeypatch.setenv("DCDNS_HOST", "TEST_HOST")
	monkeypatch.setenv("DCDNS_ZONE", "TEST_ZONE")
	monkeypatch.setenv("DCDNS_FUNCTION_URL", "https://cloudfunctions.net.mock/updateHost")
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

def test_main_max_retry(requests_mock, monkeypatch):
	# given
	monkeypatch.setenv("DCDNS_IPV4", "YES")
	monkeypatch.setenv("DCDNS_IPV6", "YES")
	monkeypatch.setenv("DCDNS_TOKEN", "TEST_TOKEN")
	monkeypatch.setenv("DCDNS_HOST", "TEST_HOST")
	monkeypatch.setenv("DCDNS_ZONE", "TEST_ZONE")
	monkeypatch.setenv("DCDNS_FUNCTION_URL", "https://cloudfunctions.net.mock/updateHost")
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