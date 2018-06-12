from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Event
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rolepermissions.checkers import has_role, has_permission
from core.roles import Respo

from core.models import Association, Event, Staff, EventStatus, Membership, MemberRole, Participant, AssociationStaff

def from_office(asso, user):
    office = Membership.objects.filter(asso=asso, role__exact=MemberRole.PRESIDENT._value_) |\
            Membership.objects.filter(asso=asso, role__exact=MemberRole.OFFICE._value_)
    return office.filter(member=user).count() != 0

def from_asso_staff(event, user):
    l = []
    for a in AssociationStaff.objects.filter(event=event):
        if from_office(a.asso, user):
            l.append(a)
    return l

def manager_check(event, user):
    staff = get_staff(event)
    if staff.filter(member=user).count() != 0:
        return True

    if has_permission(user, 'manage'):
        return True

    if from_office(event.orga, user):
        return True

    if from_asso_staff(event, user):
        return True

    if event.creator == user:
        return True

    return False

@login_required
def view(request, id):
    event = get_object_or_404(Event, id=id)

    manage = manager_check(event, request.user)

    staffs = get_staff(event)
    members = get_members(event, event.orga)
    user = request.user
    remaining_int = event.int_capacity
    remaining_ext = event.ext_capacity
    modify = False

    for s in staffs:
        if s.event == event and s.member == user:
            modify = True
            break

    for m in members:
        if m.member == user:
            modify = True
            break

    participants = Participant.objects.filter(event__exact=event)

    for p in participants:
        if "epita" in p.mail:
            remaining_int -= 1
            remaining_int = max(0, remaining_int)
        else:
            remaining_ext -= 1
            remaining_ext = max(0, remaining_ext)

    try:
        event.valid = Membership.objects.filter(asso=event.orga) \
                          .get(member=request.user) \
                          .role == MemberRole.PRESIDENT._value_
    except ObjectDoesNotExist:
        event.valid = False

    class StaffForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(StaffForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'

    class AddStaff(StaffForm):
        staff = forms.ModelChoiceField(queryset=members, required=True)


    if request.method == 'POST':
        form = AddStaff(request.POST)
        add_staff(event, form)

        return redirect(reverse('core:event', args=[event.id]))
    else:
        add_form = AddStaff()

    variables = {}
    variables['manage'] = manage
    variables['event'] = event
    variables['staff'] = staffs
    variables['members'] = members
    variables['modify'] = modify
    variables['add_form'] = add_form
    variables['remaining_int'] = remaining_int
    variables['remaining_ext'] = remaining_ext
    variables['respo'] = request.user.has_perm('core.respo')
    variables['can_register'], variables['status'] = can_register(event, request.user)
    pres = len(Membership.objects.select_related('asso') \
                        .filter(asso__exact=event.orga) \
                        .filter(member__exact=user) \
                        .filter(role__exact=3)) > 0

    variables['pres'] = pres

    return render(request, 'event.html', variables)

@login_required
def remove(request, name):
    Event.objects.get(name=name).delete()
    return redirect("core:event")

def get_staff(event):
    o = Staff.objects.select_related('event') \
        .filter(event__exact=event)

    return o

def get_members(event, asso):
    o = Membership.objects.select_related('asso') \
        .filter(asso__exact=asso) \
        .exclude(member__in=(Staff.objects.select_related('member') \
                                .filter(event__exact=event) \
                                .values('member')))

    return o

def add_staff(event, form):
    if not form.is_valid():
        return
    member = form.cleaned_data['staff']
    staff = Staff(event=event, member=member.member)
    staff.save()

def rm_staff(request, id, member):
    event = get_object_or_404(Event, id=id)
    tmp = Staff.objects.select_related('member') \
          .filter(member__username=member) \
          .filter(event__exact=event)
    tmp.delete()

    return redirect(reverse('core:event', args=[event.id]))

def count_participants(event):
    participants = Participant.objects.filter(event=event)
    ext_count = 0
    int_count = 0
    for par in participants:
        if par.is_external():
            ext_count += 1
        else:
            int_count += 1
    return (ext_count, int_count)

def can_register(event, user):
    if event.status == EventStatus.FINISHED._value_:
        return (False, 'Cet évènement est fini')

    staff = Staff.objects.filter(member=user, event=event)
    if staff.count() != 0:
        return (False, 'Vous êtes staff de cet évènement')

    office = Membership.objects.filter(asso=event.orga, role__exact=MemberRole.OFFICE._value_) |\
             Membership.objects.filter(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)
    if office.filter(member=user).count() == 1:
        return (False, 'Vous êtes membre du bureau de l\'association organisatrice')

    if Participant.objects.filter(event=event, user=user).count() == 1:
        return (False, 'Vous êtes déjà inscrit à cet évènement')

    ext_count, int_count = count_participants(event)
    if user.email.endswith('epita.fr'):
        if int_count >= event.int_capacity:
            return (False, 'Plus de places internes disponibles')
    else:
        if ext_count >= event.ext_capacity:
            return (False, 'Plus de places externes disponibles')

    if timezone.now() > event.closing:
        return (False, 'Les inscriptions sont closes')

    return (True, '')
