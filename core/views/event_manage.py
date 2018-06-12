from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from rolepermissions.checkers import has_role
from django.http import JsonResponse

from core.views.event import manager_check
from core.models import Event, Staff, MemberRole, Membership
from core.forms.event_create import event_form

def can_manage_staff(event, user):
    if has_role(user, 'respo') or user.is_superuser:
        return True

    if user == event.creator:
        return True

    office = Membership.objects.filter(asso=event.orga, role__exact=MemberRole.OFFICE._value_) |\
             Membership.objects.filter(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)
    if office.filter(member=user).count() == 1:
        return True

    return False

def prefilled_form(event):
    form = event_form(initial={
        'title': event.title,
        'orga': event.orga,
        'description': event.description,
        'start_date': event.start.date(),
        'start_time': event.start.time(),
        'end_date': event.end.date(),
        'end_time': event.end.time(),
        'place': event.place,
        'cover': event.cover,
        'closing_date': event.closing.date(),
        'closing_time': event.closing.time(),
        'int_capacity': event.int_capacity,
        'ext_capacity': event.ext_capacity,
        'int_price': event.int_price,
        'ext_price': event.ext_price,
        'display': event.display
    })
    for field in form.fields.values():
        field.widget.attrs['readonly'] = True
    return form

@login_required
def view(request, id):
    event = get_object_or_404(Event, id=id)
    if not manager_check(event, request.user):
        return redirect(reverse('core:event', args=[event.id]))

    if request.method == 'POST':
        form = event_form(request.POST, request.FILES)
        if form.is_valid():
            # FIXME
            pass
    else:
        form = prefilled_form(event)

    staff = get_staff(event)

    variables = {}
    variables['asso'] = event.orga
    variables['form'] = form
    variables['event'] = event
    variables['staff'] = staff
    variables['can_manage_staff'] = can_manage_staff(event, request.user)

    return render(request, 'event_manage.html', variables)


@login_required
def rm_staff(request):
    event_id = request.GET.get('event', None)
    staff_id = request.GET.get('staff', None)
    if event_id is None or staff_id is None:
        return redirect(reverse('core:index'))
    event = Event.objects.get(id=event_id)

    if not can_manage_staff(event, request.user):
        return redirect(reverse('core:event_manage', args=[event_id]))

    staff = Staff.objects.get(id=staff_id)
    if staff.event != event:
        return redirect(reverse('core:event_manage', args=[event_id]))

    staff.delete();

    return JsonResponse({'success': True, 'id': staff_id})

def get_staff(event):
    return Staff.objects.filter(event=event)
