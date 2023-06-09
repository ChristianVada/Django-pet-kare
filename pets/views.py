from rest_framework.views import APIView, Request, Response, status
from .models import Pet, Sex_choice
from django.forms.models import model_to_dict


class PetView(APIView):
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()

        pet_list = []

        for pet in pets:
            pets_dict = model_to_dict(pet)
            pet_list.append(pets_dict)
