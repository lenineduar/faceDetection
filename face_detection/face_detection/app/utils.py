from django.conf import settings
from pytz import timezone

def change_utc_date(date):
    date_utc = date.astimezone(timezone(settings.TIME_ZONE))
    return date_utc.strftime("%d-%m-%Y @ %H:%M:%S")