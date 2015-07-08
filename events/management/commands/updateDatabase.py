# Updates database based on information existing on Off-The-Grid's website

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from events.models import Event, Vendor, Event_Vendor

import requests, json
import datetime
import re
import time

# Command created to allow for 'python manage.py updateDatabase' calls
class Command(BaseCommand):
    help = 'Fetches all upcoming events from Off-The-Grid\'s website'

    def handle(self, *args, **options):
        updateDatabase()

# Main command for updating the database
def updateDatabase():

    start_time = time.time()

    base_url = "http://offthegridsf.com/wp-admin/admin-ajax.php?"

    # Ex.: action=otg_market&delta=1&market=41
    getter_dict = {'action': 'otg_market', 'delta': 0, 'market': 1}

    tested_max = 45
    delta_misses = 0
    market_misses = 0
    miss_limit = 3

    while market_misses < miss_limit or getter_dict['market'] < tested_max:
        hits = 0

        while delta_misses < miss_limit:
            r = requests.get(base_url, getter_dict)

            if miss(r.text):
                delta_misses += 1
            else:
                p = parseAll(r.text)
                processParse(p)
                print("delta: {0} ::: market: {1}").format(
                        getter_dict['delta'], getter_dict['market'])
                delta_misses = 0
                hits += 1

            getter_dict['delta'] += 1

        delta_misses = 0
        if hits == 0:
            market_misses += 1
        else:
            market_misses = 0

        getter_dict['market'] += 1
        getter_dict['delta'] = 0

    end_time = time.time()

    print("Run time: {0} seconds").format(end_time - start_time)

# Processes all parsed fields
def processParse(p_dict):
    event_list = []

    name = str(p_dict['details']['name'])
    address = str(p_dict['details']['address'])
    
    for i in range(len(p_dict['dates_dict']['dates'])):
        d = p_dict['dates_dict']['dates'][i]
        start = p_dict['dates_dict']['hours'][i][0]
        end = p_dict['dates_dict']['hours'][i][1]
        print("{0} {1} {2} {3} {4}").format(name, d, start, end, address)

        e = insertEvent(name, d, start, end, address)
        if e:
            event_list.append(e)

    for event in event_list:
        for vendor in p_dict['vendors'][event.date]:
            v_result = insertVendor(vendor)
            if v_result:
                insertEventVendor(event, v_result)

    return True

# Inserts an event into the database - encapsulated in try-except clause
def insertEvent(name, date, start, end, location):
    e = Event(name=name, date=date, start=start, end=end, location=location)

    try:
        e.save()
    except IntegrityError:
        print("Event already exists in database: {0}").format(e)
        e = Event.objects.filter(name=name, date=date, start=start, end=end,
                                 location=location)[0]
    except Exception as err:
        print("An error has occurred!\n{0}").format(str(err))
        e = None

    return e

# Inserts a vendor into the database - encapsulated in try-except clause
def insertVendor(name):
    v = Vendor(name=name)

    try:
        v.save()
    except IntegrityError:
        print("Vendor already exists in database: {0}").format(v)
        v = Vendor.objects.filter(name=name)[0]
    except Exception as err:
        print("An error has occurred!\n{0}").format(str(err))
        v = None

    return v

# Inserts an event_vendor into the database - encapsulated in try-except clause
def insertEventVendor(event, vendor):
    ev = Event_Vendor(event=event, vendor=vendor)

    try:
        ev.save()
    except IntegrityError:
        print("Event-Vendor already exists in database: {0}").format(ev)
        ev = Event_Vendor.objects.filter(event=event, vendor=vendor)[0]
    except Exception as err:
        print("An error has occurred!\n{0}").format(str(err))
        ev = None

    return ev

# Helper method for determining if the page has any meaningful information
def miss(text):
    classes = [
        'otg-market-data-vendors-names',
        'otg-markets-data-vendor-name-link',
        'otg-market-data-events-pagination',
    ]

    found = 0

    for c in classes:
        key_list = re.findall(r'' + c, text)
        if len(key_list) > 0:
            found += 1

    return found <= 1

# Overall function for parsing the given webpage
# - inner functions:
#   - parseDetails
#   - parseDates
#   - parseVendors
def parseAll(text):

    general_tag = r'.*?>(.*?)</'

    # Parses the event details (i.e. name, address)
    def parseDetails(text):
        detail_classes = {
            'name': 'otg-market-data-name',
            'address': 'otg-market-data-address',
        }

        name_pat = re.compile(r'' + detail_classes['name'] + general_tag,
                                 re.DOTALL)

        link_tag = r'.*?(?:<a.*?)+?'
        address_pat = re.compile(r'' + detail_classes['address'] + link_tag +
                                 general_tag, re.DOTALL)

        details = {}

        details['name'] = name_pat.search(text).group(1)
        details['address'] = address_pat.search(text).group(1)

        return details

    # Parses the event's time information (i.e. date, hours, ampm)
    def parseDates(text):
        date_classes = {
            #'day': 'otg-market-data-events-event-day',
            'hours': 'otg-market-data-events-event-hours',
            'ampm': 'otg-market-data-events-event-ampm',
            'date': 'otg-market-data-events-pagination',
        }

        date_pat = re.compile(r'' + date_classes['date'] + general_tag,
                              re.DOTALL)

        date_match = date_pat.search(text)
        split_indices = []
        dates = []

        while date_match:
            split_indices.append(date_match.end())
            dates.append(str(date_match.group(1)).strip())
            date_match = date_pat.search(text, split_indices[-1])

        if not split_indices:
            print "ERROR: Found no dates -> likely need to update date_classes"
            return False

        sep_digits_tag = r'(\d+).*?(\d+)'

        hours_pat = re.compile(r'' + date_classes['hours'] + general_tag,
                               re.DOTALL)
        hours_match = hours_pat.findall(text)

        hours = [(int(x[0]), int(x[1])) for x in
                    (re.search(sep_digits_tag, hour, re.DOTALL).groups()
                        for hour in hours_match)
                ]

        ampm_pat = re.compile(r'' + date_classes['ampm'] + general_tag,
                              re.DOTALL)
        ampm_match = ampm_pat.findall(text)

        for i in range(len(hours)):
            if ampm_match[i].lower() == 'pm':
                hours[i] = (datetime.time(hours[i][0] + 12),
                            datetime.time(hours[i][1] + 12))
            else:
                hours[i] = (datetime.time(hours[i][0]),
                            datetime.time(hours[i][1]))

        tmp = []
        for d in dates:
            year = datetime.date.today().year
            result = re.search(sep_digits_tag, d, re.DOTALL).groups()
            month = int(result[0])
            day = int(result[1])
            tmp.append(datetime.date(year, month, day))

        dates = tmp

        return {'splits': split_indices, 'dates': dates, 'hours': hours}

    # Parses the vendor's information (i.e. all vendors for a given event)
    def parseVendors(text, dates, splits):
        vendor_classes = {
            'link': 'otg-markets-data-vendor-name-link',
        }

        if not dates or not splits:
            print "ERROR: Failed to parse vendors"
            return False

        vendors = {}
        vendor_pat = re.compile(r'' + vendor_classes['link'] + general_tag,
                                re.DOTALL)

        start = splits[0]
        ptr = 1

        while ptr < len(splits):
            end = splits[ptr]
            vendors[dates[ptr-1]] = vendor_pat.findall(text[start:end])
            start = end
            ptr += 1

        vendors[dates[ptr-1]] = vendor_pat.findall(text[start:])

        return vendors


    details = parseDetails(text)

    dates_dict = parseDates(text)
    dates = dates_dict['dates']
    splits = dates_dict['splits']

    vendors = parseVendors(text, dates, splits)

    return {'vendors': vendors, 'dates_dict': dates_dict, 'details': details}
