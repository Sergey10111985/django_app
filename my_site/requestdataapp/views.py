from django.core.files.storage import FileSystemStorage
from django.forms import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result
    }

    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    return render(request, 'requestdataapp/user-bio-form.html')


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print('saves file', filename)

    return render(request, 'requestdataapp/file-upload.html')


def handle_limited_file_upload(request: HttpRequest) -> HttpResponse:
    context = {
    }
    if request.method == 'POST' and request.FILES.get('lfile'):

        myfile = request.FILES['lfile']
        if myfile.size <= 1024 * 1024:
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print('saves file', filename)
        else:
            context['file_too_large'] = 1

    return render(request, 'requestdataapp/file-upload-limit.html', context=context)
