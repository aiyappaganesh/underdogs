import time
from datetime import datetime, time as Time, timedelta
from pytz import timezone, utc
import logging

TZ_EASTERN = timezone('US/Eastern')

def is_not_ny_time_zone(tz):
    return (tz != '' and tz != 'America/New_York')

def now(tz=utc):
    return datetime.now(tz)
    
def this_minute():
    return now().replace(second=0, microsecond=0)
    
def today():
    return this_minute().replace(hour=0, minute=0)
    
def eastern_datetime(time_=None):
    time_ = time_ or now()
    return to_timezone(time_, TZ_EASTERN)

def to_utc(datetime):
    return to_timezone(datetime)

def local_datetime(time=None, tz=None):
    if not tz:
        tz = 'US/Eastern'
    now_ = now(timezone(tz))
    if time:
        return replace_time(now_, time)
    return now_

def to_timezone(datetime, tzinfo=utc):
    if not datetime:
        return datetime
    return datetime.astimezone(tzinfo) \
            if datetime.tzinfo else  tzinfo.localize(datetime)

def timestamp(datetime, local=False):
    if not local:
        return long(time.mktime(datetime.utctimetuple()))
    else:
        return long(time.mktime(datetime.timetuple()))

def eastern_time_from_timestamp(timestamp):
    return fromtimestamp(timestamp, TZ_EASTERN)

def fromtimestamp(timestamp, tzinfo=utc):
    utc_datetime = datetime.fromtimestamp(timestamp, utc)
    if tzinfo is utc:
        return utc_datetime
    return utc_datetime.astimezone(tzinfo)

def time_from_string(*hh_col_mms):
    ret_val = []
    for hh_col_mm in hh_col_mms:
        hh_part, mm_part = hh_col_mm.split(":")
        ret_val.append(Time(int(hh_part), int(mm_part)))
    return ret_val[0] if len(ret_val) == 1 else ret_val

def date_from_string(*mm_dd_yyyys):
    ret_val = []
    for mm_dd_yyyy in mm_dd_yyyys:
        mm_part, dd_part, yyyy_part = mm_dd_yyyy.split("-")
        ret_val.append(datetime(int(yyyy_part), int(mm_part), int(dd_part)))
    return ret_val[0] if len(ret_val) == 1 else ret_val

def replace_time(datetime_, time_):
    new_datetime = datetime.combine(datetime_.date(), time_)
    return to_timezone(new_datetime, datetime_.tzinfo) if datetime_.tzinfo \
        else new_datetime

def get_data_timestamp(last_updated):
    dt = last_updated -  timedelta(days=30)
    return long(time.mktime(dt.utctimetuple()))

