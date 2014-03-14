from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from registro.models import Message


@login_required
def dashboard(req):
    num_sent = Message.objects.filter(direction='O').count()
    num_received = Message.objects.filter(direction='I').count()
    return render_to_response("painel.html", {"num_sent": num_sent, "num_received": num_received}, context_instance=RequestContext(req))