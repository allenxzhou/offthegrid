# 'Events' Views

from django.shortcuts import render, get_object_or_404

from .models import Event, Vendor, Event_Vendor
import datetime

# Default page - limits number of future events shown to 2 weeks
def index(request):
    future_marker = datetime.datetime.now() + datetime.timedelta(14)
    events_list = Event.objects.filter(date__lte=future_marker, \
                  date__gt=datetime.datetime.now()).order_by('date')
    context = {'events': events_list}

    return render(request, 'events/index.html', context)

# Event details page - shows the vendors at the given event
def details(request, event_name, event_date):
    e = Event.objects.filter(name=event_name, date=event_date)[0]

    ev_list = Event_Vendor.objects.filter(event=e)
    vendors = [ev.vendor for ev in ev_list]
    context = {'vendors': vendors, 'event': e}

    return render(request, 'events/details.html', context)

# Individual vendor page - shows past and future counts, along with events
def vendor(request, vendor_name, days=30):
    v = Vendor.objects.filter(name=vendor_name)[0]
    curr_marker = datetime.datetime.now()
    past_marker = curr_marker - datetime.timedelta(days)

    past_list = Event_Vendor.objects.filter(vendor=v, \
                event__date__lte=curr_marker, event__date__gte=past_marker) \
                .order_by('event__date').reverse()[:20]
    past_list = [p.event for p in past_list]

    future_list = Event_Vendor.objects.filter(vendor=v, \
                  event__date__gt=curr_marker).order_by('event__date')
    future_list = [f.event for f in future_list]

    context = {'name': vendor_name,
               'past_list': past_list, 'past_count': len(past_list),
               'future_list': future_list, 'future_count': len(future_list)}

    return render(request, 'events/vendor.html', context)

# All vendors page - displays them in order
def vendors(request, days=30):
    vendor_list = Vendor.objects.all()
    curr_marker = datetime.datetime.now()
    past_marker = curr_marker - datetime.timedelta(days)

    counts = {}

    for v in vendor_list:
        ev_list = Event_Vendor.objects.filter(vendor=v, \
                  event__date__lte=curr_marker, event__date__gte=past_marker)

        counts[v.name] = len(ev_list)

    vendors = []
    for k in sorted(counts, key=counts.get, reverse=True):
        vendors.append((k, counts[k]))

    return render(request, 'events/vendors.html', {'vendors': vendors})

