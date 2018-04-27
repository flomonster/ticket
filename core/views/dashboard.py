"""@package views
This module is intended to display the dashboard of an association.

It will allow the user to manage an association through various
features.
"""
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User

from core.models import Association, Event, Membership, MemberRole, EventStatus


class Dashboard:
    msg = None

    @staticmethod
    def view(request, name):
        """
        @brief display the dashboard of an association if it exists.
        @param request request for the current page.
        @param name name of the requested association.
        @return an HttpResponse serving the web page.
        """
        asso = get_object_or_404(Association, name=name)

        # Prepare useful queryset
        simples = Dashboard.get_members(asso, MemberRole.SIMPLE)
        office = Dashboard.get_members(asso, MemberRole.OFFICE)
        president = Dashboard.get_members(asso, MemberRole.PRESIDENT)

        all = simples | office | president
        others = User.objects.all().exclude(pk__in=all.values('member'))

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
            role = forms.ChoiceField(choices=MemberRole.choices())

        class RemoveForm(AssoForm):
            membre = forms.ModelChoiceField(queryset=all,
                                            required=True)

        if request.method == 'POST':
            if 'officeModal' in request.POST:
                form = OfficeForm(request.POST)
                Dashboard.add_office_member(asso, form)
            elif 'addModal' in request.POST:
                form = AddForm(request.POST)
                Dashboard.add_member(asso, form)
            else:
                form = RemoveForm(request.POST)
                Dashboard.remove_member(asso, form)

            if Dashboard.msg:
                return redirect(reverse('core:association', args=[asso.name]))

        else:
            office_form = OfficeForm()
            add_form = AddForm()
            remove_form = RemoveForm()

        # Creating templates variables
        variables = {}
        variables['events'] = Dashboard.related_events(asso)
        variables['office'] = office
        variables['asso'] = asso
        variables['info'] = Dashboard.msg

        variables['office_form'] = office_form
        variables['add_form'] = add_form
        variables['remove_form'] = remove_form

        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)

        Dashboard.msg = None

        return render(request, 'dashboard.html', variables)

    @staticmethod
    def related_events(asso):
        """
        @brief search for the events related to an association.
        @param asso query object of the requested association.
        @return a query set of all the related events.
        """
        e = Event.objects.select_related('orga') \
            .filter(orga__exact=asso) \
            .order_by('start')
        return e

    @staticmethod
    def add_office_member(asso, form):
        """
        @brief update membership to OFFICE role
        @param asso association to update
        @param form form with the requested update
        """
        if not form.is_valid():
            return None

        member = form.cleaned_data['membre']
        member.role = MemberRole.OFFICE._value_
        member.save()

        user = member.member.username

        Dashboard.msg = user + ' a bien été ajouté au bureau.'

    @staticmethod
    def remove_member(asso, form):
        """
        @brief completely remove a membership row
        @param asso association to update
        @param form form with the update
        """
        if not form.is_valid():
            return

        member = form.cleaned_data['membre']
        user = member.member.username
        member.delete()

        Dashboard.msg = user + " a bien été supprimé de l'association"

    @staticmethod
    def add_member(asso, form):
        """
        @brief add a new membership row
        @param asso association of the new membership
        @param form form with the member
        """
        if not form.is_valid():
            return

        member = form.cleaned_data['membre']
        role = form.cleaned_data['role']
        membership = Membership(asso=asso, member=member, role=role)
        membership.save()

        Dashboard.msg = member.username + " a bien été ajouté à l'association."

    @staticmethod
    def get_members(asso, role):
        o = Membership.objects.select_related('asso') \
            .filter(asso__exact=asso) \
            .filter(role__exact=str(role._value_))

        return o

    @staticmethod
    def delete_office_view(request, name, member):
        """
        @brief delete a member from the office of an association.
        @param request http request
        @param name name of the association
        @param member user object of the member to add
        @return redirection to dashboard
        """
        asso = get_object_or_404(Association, name=name)
        office = Dashboard.get_members(asso, MemberRole.OFFICE) \
            .select_related('member') \
            .get(member__username=member)

        office.role = str(MemberRole.SIMPLE._value_)
        office.save()
        Dashboard.msg = member + ' a bien été supprimé du bureau.'

        return redirect(reverse('core:association', args=[asso.name]))
