"""@package views
This module is intended to display the dashboard of an association.

It will allow the user to manage an association through various
features.
"""
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect

from core.models import Association, Event, Membership, MemberRole



class Dashboard:
    msg = ''

    @staticmethod
    def view(request, name):
        """
        @brief display the dashboard of an association if it exists.
        @param request request for the current page.
        @param name name of the requested association.
        @return an HttpResponse serving the web page.
        """
        asso = get_object_or_404(Association, name=name)

        # Select simple members
        o = Membership.objects.select_related('asso') \
            .filter(asso__exact=asso)\
            .filter(role__exact=str(MemberRole.SIMPLE._value_))

        # Nested class Form for the association
        class OfficeForm(forms.Form):
            membre = forms.ModelChoiceField(queryset=o, required=True)

            def __init__(self, *args, **kwargs):
                super(OfficeForm, self).__init__(*args, **kwargs)
                for field_name, field in self.fields.items():
                    field.widget.attrs['class'] = 'form-control'

        if request.method == 'POST':
            form = OfficeForm(request.POST)
            if form.is_valid():
                # Add a member to office
                form.cleaned_data['membre'].role = MemberRole.OFFICE._value_
                form.cleaned_data['membre'].save()
                user = form.cleaned_data['membre'].member

                Dashboard.msg = user.username + ' a bien été ajouté au bureau.'
                return redirect(reverse('core:association', args=[asso.name]))
        else:
            form = OfficeForm()

        # Creating templates variables
        variables = {}
        variables['events'] = Dashboard.related_events(asso)
        variables['office'] = Dashboard.get_office_members(asso)
        variables['asso'] = asso
        variables['info'] = Dashboard.msg
        variables['form'] = form

        Dashboard.msg = ''

        return render(request, 'dashboard.html', variables)

    @staticmethod
    def get_office_members(asso):
        """
        @brief search for the members that are part of the office.
        @param asso the association.
        @return a query set of all the office members.
        """
        o = Membership.objects.select_related('asso') \
            .filter(asso__exact=asso)\
            .filter(role__exact=str(MemberRole.OFFICE._value_))

        return o


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
    def delete_office_view(request, name, member):
        """
        @brief delete a member from the office of an association.
        @param request http request
        @param name name of the association
        @param member user object of the member to add
        @return redirection to dashboard
        """
        asso = get_object_or_404(Association, name=name)

        o = Membership.objects.select_related('asso') \
            .filter(asso__exact=asso) \
            .filter(role__exact=str(MemberRole.OFFICE._value_)) \
            .select_related('member') \
            .get(member__username=member)

        o.role = str(MemberRole.SIMPLE._value_)
        o.save()
        Dashboard.msg = member + ' a bien été supprimé du bureau.'

        return redirect(reverse('core:association', args=[asso.name]))
