from .models import Operation, Vector
from django.shortcuts import render
import json


def index(request):
    vectors = Vector.objects.all()
    operations = Operation.objects.all()
    vids = json.dumps({"vids": list(vectors.values_list('id', flat=True))})
    oids = json.dumps({"oids": list(operations.values_list('id', flat=True))})
    return render(request, "index.html", 
    {"vectors": vectors,
     "operations": operations,
     "vids": vids,
     "oids": oids}
     )

