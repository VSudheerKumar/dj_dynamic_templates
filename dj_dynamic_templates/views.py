from django.shortcuts import render

from .models import *

# Create your views here.
def mail_template_view(request, template_code):
    return render(request, MailTemplate.objects.get(is_active=True, code=template_code).get_template_render_path())