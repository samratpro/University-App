from .models import Logo  # Adjust the import path if needed

def logo_context(request):
    logo = Logo.objects.first()
    return {'logos': logo}
