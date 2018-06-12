from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from rolepermissions.checkers import has_role
from django.http import JsonResponse

from core.views.event import manager_check
from core.models import Event, Staff, MemberRole, Membership

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

@login_required
def view(request, id):
    event = get_object_or_404(Event, id=id)
    if not manager_check(event, request.user):
        return redirect(reverse('core:event', args=[event.id]))

    staff = get_staff(event)

    variables = {}
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
