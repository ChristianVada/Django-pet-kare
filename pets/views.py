from rest_framework.views import APIView, Request, Response, status
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


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

        trait = request.query_params.get("trait", None)

        if trait:
            pets = pets.filter(traits__name=trait)

        result_page = self.paginate_queryset(pets, request)

        serializer_format = PetSerializer(instance=result_page, many=True)

        return self.get_paginated_response(serializer_format.data)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)

            serializer_format = PetSerializer(instance=pet)

            return Response(data=serializer_format.data, status=status.HTTP_200_OK)

        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)

            pet.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

    def patch(self, request: Request, pet_id: int) -> Response:
        serializer_validated = PetSerializer(data=request.data, partial=True)

        pet = get_object_or_404(Pet, id=pet_id)

        serializer_validated.is_valid(raise_exception=True)

        group_data = serializer_validated.validated_data.pop("group", None)

        if group_data:
            try:
                group_find = Group.objects.get(
                    scientific_name__iexact=group_data["scientific_name"]
                )

            except Group.DoesNotExist:
                group_find = Group.objects.create(**group_data)

            pet.group = group_find

        trait_data = serializer_validated.validated_data.pop("traits", None)

        if trait_data:
            pet.traits.clear()

            for trait_dict in trait_data:
                trait_obj = Trait.objects.filter(
                    name__iexact=trait_dict["name"]
                ).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait_dict)
                pet.traits.add(trait_obj)

        for key, value in serializer_validated.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer_format = PetSerializer(instance=pet)

        return Response(serializer_format.data, status.HTTP_200_OK)
