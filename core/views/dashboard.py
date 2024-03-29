"""@package views
This module is intended to display the dashboard of an association.

It will allow the user to manage an association through various
features.
"""
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rolepermissions.checkers import has_role, has_object_permission

from core.models import Association, Event, Membership, MemberRole, EventStatus


class Dashboard:
    msg = None
    error = None

    ##
    # @brief display the dashboard of an association if it exists.
    # @param request request for the current page.
    # @param name name of the requested association.
    # @return an HttpResponse serving the web page.
    @staticmethod
    @login_required
    def view(request, name):
        asso = get_object_or_404(Association, name=name)
        flag = not request.user.is_superuser and not has_role(request.user, 'respo')
        if flag:
            member = get_object_or_404(
                Membership, member=request.user, asso=asso)
        else:
            member = None

        # Prepare useful queryset
        simples = Dashboard.get_members(asso, MemberRole.SIMPLE)
        office = Dashboard.get_members(asso, MemberRole.OFFICE)
        president = Dashboard.get_members(asso, MemberRole.PRESIDENT)

        all = simples | office | president
        others = User.objects.all().exclude(pk__in=all.values('member'))
        office = office | president

        # Nested classes in order to create forms with different behaviours
        class AssoForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super(AssoForm, self).__init__(*args, **kwargs)
                for field_name, field in self.fields.items():
                    field.widget.attrs['class'] = 'form-control'

        class OfficeForm(AssoForm):
            membre = forms.ModelChoiceField(queryset=simples, required=True)

        class AddForm(AssoForm):
            membre = forms.ModelChoiceField(queryset=others, required=True)

        class RemoveForm(AssoForm):
            membre = forms.ModelChoiceField(queryset=all, required=True)

        class PresForm(AssoForm):
            membre = forms.ModelChoiceField(
                queryset=(simples | office
                          ).exclude(role__exact=MemberRole.PRESIDENT._value_),
                required=True)

        if request.method == 'POST':
            if 'officeModal' in request.POST:
                form = OfficeForm(request.POST)
                Dashboard.add_office_member(asso, form)

            elif 'addModal' in request.POST:
                form = AddForm(request.POST)
                Dashboard.add_member(asso, form)

            elif 'presidentModal' in request.POST:
                form = PresForm(request.POST)
                Dashboard.designate_president(asso, form)

            else:
                form = RemoveForm(request.POST)
                Dashboard.remove_member(asso, form)

            if Dashboard.msg:
                return redirect(reverse('core:association', args=[asso.name]))

        else:
            office_form = OfficeForm()
            add_form = AddForm()
            remove_form = RemoveForm()
            president_form = PresForm()

        # Creating templates variables
        variables = {}
        variables['can_add_office'] = has_object_permission(
            'add_office', request.user, asso)
        variables['can_remove_office'] = variables['can_add_office']
        variables['can_manage_members'] = has_object_permission(
            'validate_member', request.user, asso)
        variables['events'] = Dashboard.related_events(asso)
        variables['office'] = office
        variables['asso'] = asso
        variables['info'] = Dashboard.msg
        variables['fail'] = Dashboard.error
        variables['respo'] = has_role(request.user, 'respo')
        variables[
            'pres'] = True if member is None else member.role == MemberRole.PRESIDENT._value_

        variables['office_form'] = office_form
        variables['add_form'] = add_form
        variables['remove_form'] = remove_form
        variables['president_form'] = president_form

        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)
        variables['rejected'] = str(EventStatus.REJECTED._value_)

        Dashboard.msg = None

        return render(request, 'dashboard.html', variables)

    ##
    # @brief search for the events related to an association.
    # @param asso query object of the requested association.
    # @return a query set of all the related events.
    @staticmethod
    def related_events(asso):
        e = Event.objects.select_related('orga') \
            .filter(orga__exact=asso) \
            .exclude(status__exact=EventStatus.FINISHED._value_)\
            .exclude(status__exact=EventStatus.REJECTED._value_)\
            .order_by('start')
        return e

    ##
    # @brief update membership to OFFICE role
    # @param asso association to update
    # @param form form with the requested update
    @staticmethod
    def add_office_member(asso, form):
        if not form.is_valid():
            return None

        member = form.cleaned_data['membre']
        member.role = MemberRole.OFFICE._value_
        member.save()

        user = member.member.username

        Dashboard.msg = user + ' a bien été ajouté au bureau.'

    @staticmethod
    def designate_president(asso, form):
        if not form.is_valid():
            return None

        try:
            old = Membership.objects.get(
                asso=asso, role__exact=MemberRole.PRESIDENT._value_)
            old.role = MemberRole.OFFICE._value_
            old.save()
        except:
            pass

        member = form.cleaned_data['membre']
        member.role = MemberRole.PRESIDENT._value_
        member.save()

        Dashboard.msg = member.member.username + ' a bien été nommé président.'

    ##
    # @brief completely remove a membership row
    # @param asso association to update
    # @param form form with the update
    @staticmethod
    def remove_member(asso, form):
        if not form.is_valid():
            return

        member = form.cleaned_data['membre']
        user = member.member.username
        member.delete()

        Dashboard.msg = user + " a bien été supprimé de l'association"

    ##
    # @brief add a new membership row
    # @param asso association of the new membership
    # @param form form with the member
    @staticmethod
    def add_member(asso, form):
        if not form.is_valid():
            return

        member = form.cleaned_data['membre']
        membership = Membership(
            asso=asso, member=member, role=MemberRole.SIMPLE._value_)
        membership.save()

        Dashboard.msg = member.username + " a bien été ajouté à l'association."

    @staticmethod
    def get_members(asso, role):
        o = Membership.objects.select_related('asso') \
            .filter(asso__exact=asso) \
            .filter(role__exact=str(role._value_))

        return o

    ##
    # @brief delete a member from the office of an association.
    # @param request http request
    # @param name name of the association
    # @param member user object of the member to add
    # @return redirection to dashboard
    @staticmethod
    def delete_office_view(request, name, member):
        asso = get_object_or_404(Association, name=name)
        office = Dashboard.get_members(asso, MemberRole.OFFICE)
        pres = Dashboard.get_members(asso, MemberRole.PRESIDENT)

        tmp = (office | pres).select_related('member') \
                             .get(member__username=member)

        tmp.role = str(MemberRole.SIMPLE._value_)
        tmp.save()
        Dashboard.msg = member + ' a bien été supprimé du bureau.'

        return redirect(reverse('core:association', args=[asso.name]))

    ##
    # @brief Confirm an event.
    # @param request HTTP request.
    # @param name name of the association that created the event.
    # @param id id of the event to confirm.
    # @return redirection to the confirmed event.
    @staticmethod
    def confirm_event(request, name, id):
        asso = get_object_or_404(Association, name=name)
        event = Event.objects.all().get(pk=id)

        if has_role(request.user, 'respo'):
            event.respo = True
        else:
            event.pres = True

        if event.pres and event.respo:
            event.status = EventStatus.VALIDATED._value_
        event.save()

        Dashboard.msg = "L'évènement " + event.title + ' a été confirmé.'
        return redirect(reverse('core:event', args=[event.id]))

    ##
    # @brief Reject an event.
    # @param request HTTP request.
    # @param name name of the association that created the event.
    # @param id id of the event to reject.
    # @return redirection to the list of events.
    @staticmethod
    def reject_event(request, name, id):
        asso = get_object_or_404(Association, name=name)
        event = Event.objects.all().get(pk=id)
        event.status = EventStatus.REJECTED._value_
        event.save()

        Dashboard.msg = "L'évènement " + event.title + ' a été rejeté.'
        return redirect(reverse('core:my_events'))
