from django.shortcuts import render

class MyEvents:
    @staticmethod
    def view(request):
        return render(request, 'my_events.html', {})