import random
from collections import defaultdict
from ripper.context import Context
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS

def classify_host_status(val):
    """Classifies the status of the host based on the regional node information from check-host.net"""
    if val is None:
        return HOST_IN_PROGRESS_STATUS
    try:
        if isinstance(val, list) and len(val) > 0:
            if 'error' in val[0]:
                return HOST_FAILED_STATUS
            if 'time' in val[0]:
                return HOST_SUCCESS_STATUS
    except:
        pass
    return None


def count_host_statuses(distribution):
    """Counter of in progress / failed / successful statuses based on nodes from check-host.net"""
    host_statuses = defaultdict(int)
    for val in distribution.values():
        status = classify_host_status(val)
        host_statuses[status] += 1
    return host_statuses


def fetch_zipped_body(_ctx: Context, url: str):
    """Fetches response body in text of the resource with gzip"""
    http_headers = _ctx.headers
    http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()
    compressed_resp = urllib.request.urlopen(
        urllib.request.Request(url, headers=http_headers)).read()
    return gzip.decompress(compressed_resp).decode('utf8')


def fetch_host_statuses(_ctx: Context):
    """Fetches regional availability statuses"""
    statuses = {}
    try:
        # request_code is some sort of trace_id which is provided on every request to master node
        request_code = re.search(r"get_check_results\(\n* *'([^']+)", fetch_zipped_body(_ctx, f'https://check-host.net/check-tcp?host={_ctx.host_ip}'))[1]
        # it takes time to poll all information from slave nodes
        time.sleep(5)
        # to prevent loop, do not wait for more than 30 seconds
        for i in range(0, 5):
            time.sleep(5)
            resp_data = json.loads(fetch_zipped_body(_ctx, f'https://check-host.net/check_result/{request_code}'))
            statuses = count_host_statuses(resp_data)
            if HOST_IN_PROGRESS_STATUS not in statuses:
                return statuses
    except Exception as e:
        pass
    return statuses