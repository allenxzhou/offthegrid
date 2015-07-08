from django.shortcuts import render, get_object_or_404

from .models import Event, Vendor, Event_Vendor

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

