from django.shortcuts import render, get_object_or_404

from .models import Event, Vendor, Event_Vendor
import datetime

# Create your views here.
def index(request):
    events_list = Event.objects.order_by('date')[:5]
    context = {'events': events_list}

    return render(request, 'events/index.html', context)

def details(request, event_name, event_date):
    e = Event.objects.filter(name=event_name, date=event_date)

    ev_list = Event_Vendor.objects.filter(event=e)

    return render(request, 'events/details.html', {'ev_list': ev_list})

def vendor(request, vendor_name):
    v = Vendor.objects.filter(name=vendor_name)[0]

    ev_list = Event_Vendor.objects.filter(vendor=v).order_by('event__date')
    context = {'name': vendor_name, 'ev_list': ev_list, 'count': len(ev_list)}

    return render(request, 'events/vendor.html', context)

def vendors(request, days=30):
    vendor_list = Vendor.objects.all()
    curr_marker = datetime.datetime.now()
    past_marker = curr_marker - datetime.timedelta(days)

    counts = {}

    for v in vendor_list:
        ev_list = Event_Vendor.objects.filter(vendor=v,
                  events__date__lte=curr_marker, events__date__gte=past_marker)

        counts[v.name] = len(ev_list)

    vendors = []
    for k in sorted(counts, key=counts.get, reverse=True):
        vendors.append((k, counts[k]))

    return render(request, 'events/vendors.html', {'vendors': vendors})

