from django import forms
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.core.validators import MinValueValidator

from core.views.event import manager_check, from_asso_staff
from core.models import Event, Staff, MemberRole, Membership, EventStatus, Association, Participant, AssociationStaff
from core.forms.event_create import event_form

@login_required
def add_other_staff(request):
    event_id = request.GET.get('event', None)
    member_id = request.GET.get('member_id', None)
    email = request.GET.get('email', None)
    asso_id = request.GET.get('asso', None)

    if None in [event_id, member_id, email, asso_id]:
        return redirect(reverse('core:index'))

    asso = Association.objects.get(id=asso_id)
    member = Membership.objects.get(id=member_id).member
    event = Event.objects.get(id=event_id)

    s = Staff(asso=asso, member=member, event=event, email=email)
    s.save()

    return JsonResponse({'success': True})

def can_manage_staff(event, user):
    if timezone.now() > event.start:
        return False

    if has_role(user, 'respo') or user.is_superuser:
        return True

    if user == event.creator:
        return True

    office = Membership.objects.filter(asso=event.orga, role__exact=MemberRole.OFFICE._value_) |\
             Membership.objects.filter(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)
    if office.filter(member=user).count() == 1:
        return True

    return False

def can_edit(event, user):
    return event.creator == user and timezone.now() < event.closing

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

def notify_total(event):
    pres = Membership.objects.get(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)
    dests = [pres.member.email]
    for resp in User.objects.all():
        if has_role(resp, 'respo'):
            dests.append(resp.email)
    email = EmailMessage(
        'Modification de l\'évènement ' + event.title,
        'Bonjour, un évènement de l\'association ' + event.orga.name
        + ' a été modifié'
        + '. Vous devez le revalider à nouveau.',
        'ticket.choisir.epita@gmail.com',
        dests,
    )
    email.send(fail_silently=False)

def notify_partial(event):
    pres = Membership.objects.get(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)
    email = EmailMessage(
        'Modification de l\'évènement ' + event.title,
        'Bonjour, un évènement de l\'association ' + event.orga.name
        + ' a été modifié'
        + '. Vous devez le revalider à nouveau.',
        'ticket.choisir.epita@gmail.com',
        [pres.member.email],
    )
    email.send(fail_silently=False)

def notify_participants(event):
    participants = Participant.objects.filter(event=event)
    dests = []
    for par in participants:
        dests.append(par.user.email)
    email = EmailMessage(
        'Modification de l\'évènement ' + event.title,
        'Bonjour, auquel vous participez ' + event.orga.name
        + ' a été modifié'
        + '. Cet évènement doit être revalidé.',
        'ticket.choisir.epita@gmail.com',
        dests,
    )
    email.send(fail_silently=False)

def edit(event, form):
    total = False
    partial = False
    def update(field, total=False):
        if field in ['start', 'end', 'closing']:
            if (str(form.cleaned_data[field]) + '+00:00') != str(getattr(event, field)):
                print('Hello')
                setattr(event, field, form.cleaned_data[field])
                return True
            return total
        if form.cleaned_data[field] != getattr(event, field):
            setattr(event, field, form.cleaned_data[field])
            return True
        return total

    start_date = form.cleaned_data['start_date']
    start_time = form.cleaned_data['start_time'][:5]
    form.cleaned_data['start'] = datetime.strptime(start_date + ' ' + start_time, '%Y-%m-%d %H:%M')

    end_date = form.cleaned_data['end_date']
    end_time = form.cleaned_data['end_time'][:5]
    form.cleaned_data['end'] = datetime.strptime(end_date + ' ' + end_time, '%Y-%m-%d %H:%M')

    closing_date = form.cleaned_data['closing_date']
    closing_time = form.cleaned_data['closing_time'][:5]
    form.cleaned_data['closing'] = datetime.strptime(closing_date + ' ' + closing_time, '%Y-%m-%d %H:%M')

    total = update('title', total)
    total = update('place', total)
    total = update('int_capacity', total)
    total = update('ext_capacity', total)
    total = update('start', total)
    total = update('end', total)
    total = update('closing', total)
    partial = update('int_price', partial)
    partial = update('ext_price', partial)
    update('description')
    update('display')

    if total:
        event.status = EventStatus.WAITING._value_
        event.respo = False
        event.pres = False
        notify_total(event)
        notify_participants(event)
    elif partial:
        event.status = EventStatus.WAITING._value_
        event.pres = False
        notify_partial(event)
        notify_participants(event)

    event.save()

def get_members(event, asso):
    o = Membership.objects.select_related('asso') \
        .filter(asso__exact=asso) \
        .exclude(member__in=(Staff.objects.select_related('member') \
                                .filter(event__exact=event) \
                                .values('member')))
    return o

def get_assos(event):
    o = Association.objects\
    .exclude(id=event.orga.id)\
    .exclude(id__in=(AssociationStaff.objects.select_related('asso')\
                                                    .filter(event__exact=event)\
                                                    .values('asso')))
    return o

def add_staff(event, staff):
    s = Staff(event=event, member=staff.member, asso=event.orga)
    s.save()

def add_asso_staff(event, asso, capacity):
    s = AssociationStaff(event=event, asso=asso, capacity=capacity)
    s.save()

@login_required
def view(request, id):
    event = get_object_or_404(Event, id=id)
    if not manager_check(event, request.user):
        return redirect(reverse('core:event', args=[event.id]))

    class Form(forms.Form):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'

    class StaffForm(Form):
        staff = forms.ModelChoiceField(queryset=get_members(event, event.orga), required=True)

    class AssoForm(Form):
        association = forms.ModelChoiceField(queryset=get_assos(event), required=True)
        nombre = forms.IntegerField(label='Capacité', initial=1, validators=[MinValueValidator(1)])


    if request.method == 'POST':
        if 'assos-modal' in request.POST:
            form = AssoForm(request.POST)
            if form.is_valid() and request.user == event.creator:
                add_asso_staff(event, form.cleaned_data['association'], form.cleaned_data['nombre'])
                return redirect(reverse('core:event_manage', args=[event.id]))

        if 'staff-modal' in request.POST:
            form = StaffForm(request.POST)
            if form.is_valid():
                add_staff(event, form.cleaned_data['staff'])
                return redirect(reverse('core:event_manage', args=[event.id]))

        form = event_form(request.POST, request.FILES)
        if form.is_valid() and can_edit(event, request.user):
            edit(event, form)
            return redirect(reverse('core:event', args=[event.id]))
    else:
        form = prefilled_form(event)

    staff = get_staff(event)

    variables = {}
    variables['office'] = from_asso_staff(event, request.user)
    variables['is_staff'] = is_staff(event, request.user)
    for off in variables['office']:
        off.staffs = list(Staff.objects.filter(event=event, asso=off.asso))
        diff = off.capacity - len(off.staffs)
        off.staffs += list(range(diff))
        off.members = Membership.objects.filter(asso=off.asso)
        members = [k['member'] for k in list(Staff.objects.filter(event=event, asso=off.asso).values('member'))]
        off.members = off.members.exclude(member__id__in=members)
        off.field = forms.ModelChoiceField(queryset=off.members)
        off.field.widget.attrs['class'] = 'form-control'
        off.field = off.field.widget.render('member', '')
    variables['asso'] = event.orga
    variables['form'] = form
    variables['event'] = event
    variables['staff'] = staff
    variables['assos'] = AssociationStaff.objects.filter(event=event)
    variables['can_manage_staff'] = can_manage_staff(event, request.user)
    variables['staff_form'] = StaffForm()
    variables['asso_staff_form'] = AssoForm()
    variables['can_edit'] = can_edit(event, request.user)
    variables['creator'] = request.user == event.creator
    variables['can_add_asso'] = variables['creator'] and timezone.now() < event.start
    variables['can_add_staff'] = timezone.now() < event.start

    return render(request, 'event_manage.html', variables)

def is_staff(event, user):
    staff = Staff.objects.filter(event=event, member=user)

    return staff.count() == 1 or has_role(user, 'respo')\
            or user.is_superuser or user == event.creator


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
