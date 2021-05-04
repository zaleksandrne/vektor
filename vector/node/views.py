from .models import Operation, Vector
from django.shortcuts import render

def index(request):
    vectors = Vector.objects.all()
    operations = Operation.objects.all()
    return render(
         request,
         "index.html",
         {"vectors": vectors, "operations": operations}
     )
