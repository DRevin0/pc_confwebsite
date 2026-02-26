from django.shortcuts import render

def stub(request):
    return render(request, 'main/maintenance.html')

def about(request):
    return render(request, 'main/about.html')