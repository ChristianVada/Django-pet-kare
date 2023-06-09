from rest_framework.views import APIView, Request, Response, status
from .models import Pet
from django.forms.models import model_to_dict
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer_validated = PetSerializer(data=request.data)

        serializer_validated.is_valid(raise_exception=True)

        group_data = serializer_validated.validated_data.pop("group")

        trait_data = serializer_validated.validated_data.pop("traits")

        group_find = Group.objects.filter(
            scientific_name__iexact=group_data["scientific_name"]
        ).first()

        if not group_find:
            group_find = Group.objects.create(**group_data)

        pet = Pet.objects.create(
            **serializer_validated.validated_data, group=group_find
        )

        for trait_dict in trait_data:
            trait_obj = Trait.objects.filter(name__iexact=trait_dict["name"]).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet.traits.add(trait_obj)

        serializer_format = PetSerializer(instance=pet)

        return Response(data=serializer_format.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)

        serializer_format = PetSerializer(instance=result_page, many=True)

        return self.get_paginated_response(serializer_format.data)
