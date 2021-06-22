import os
import platform
import subprocess
from datetime import datetime, time, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Network timeouts in seconds
DEFAULT_TIMEOUT = 5
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],  # http://httpstat.us/
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
USER_AGENT += 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'

# Constant Date variables
CURRENT_DAY = datetime.today()
THREE_MONTHS_BEFORE = CURRENT_DAY - timedelta(days=90)
SIX_MONTHS_BEFORE = CURRENT_DAY - timedelta(days=180)
YEAR_BEFORE = CURRENT_DAY - timedelta(days=365)

# Timestamps
CURRENT_DAY_TS = datetime.timestamp(CURRENT_DAY)
THREE_MONTHS_BEFORE_TS = datetime.timestamp(THREE_MONTHS_BEFORE)
SIX_MONTHS_BEFORE_TS = datetime.timestamp(SIX_MONTHS_BEFORE)
YEAR_BEFORE_TS = datetime.timestamp(YEAR_BEFORE)


# Returns 1st, 13th, 22nd or 3rd suffix before dates.
def date_suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


# used in lieu with date_suffix
def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + date_suffix(t.day))


def is_time_between(begin_time, end_time, check_time=None):
    begin_time = time(begin_time[0], begin_time[1])
    end_time = time(end_time[0], end_time[1])
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return False


def get_start_end_date():
    final_start_date = ''
    start_date_human_readble = ''
    final_end_date = ''
    end_date_human_readble = ''

    try:
        today = datetime.today()
        five_days_ago = today - timedelta(days=5)

        start_date = input(
            "Start Date (YYYY-MM-DD): ").strip() or five_days_ago.strftime('%Y-%m-%d')

        end_date = input(
            "End Date (YYYY-MM-DD): ").strip() or today.strftime('%Y-%m-%d')

        if start_date != '':
            start_date = start_date.replace('/', '-')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            final_start_date = start_date.strftime('%Y-%m-%d')
            start_date_human_readble = custom_strftime(
                '{S} %A %B, %Y', start_date)

        if end_date != '':
            end_date = end_date.replace('/', '-')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            final_end_date = end_date.strftime('%Y-%m-%d')
            end_date_human_readble = custom_strftime(
                '{S} %A %B, %Y', end_date)

    except Exception as e:
        print(e)
        final_start_date = five_days_ago.strftime('%Y-%m-%d')
        start_date_human_readble = custom_strftime(
            '{S} %A %B, %Y', five_days_ago)

        final_end_date = today.strftime('%Y-%m-%d')
        end_date_human_readble = custom_strftime(
            '{S} %A %B, %Y', today)

    start_end_date = {
        'start_date': [final_start_date, start_date_human_readble],
        'end_date': [final_end_date, end_date_human_readble]
    }

    return start_end_date


def clear_screen():
    command = "cls" if platform.system().lower() == "windows" else "clear"
    return subprocess.call(command, shell=True)


# To set default timeout parameter for our scrapper
# Refer: https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/#request-hooks
class EquityIndiaHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]

        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout

        return super().send(request, **kwargs)
