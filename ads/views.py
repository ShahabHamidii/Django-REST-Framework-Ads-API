from django.core import paginator
from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from .permissions import IsPublishedOrReadOnly
from .models import Ad
from .serializers import AdSerializer
from .pagination import StandardResultsSetPagination


class AdView(APIView, StandardResultsSetPagination):
    serializer_class = AdSerializer

    def get(self, request):
        queryset = Ad.objects.filter(is_public=True)
        page = self.paginate_queryset(queryset, request)
        serializer = AdSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class AdCreateView(APIView):
    serializer_class = AdSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = AdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['publisher'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdDetailView(APIView):
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsPublishedOrReadOnly)
    parser_classes = (MultiPartParser,)

    def get_object(self):
        obj = get_object_or_404(Ad.objects.filter(is_public=True), id=self.kwargs['pk'])
        self.check_object_permission(self.request, obj)
        return obj

    def get(self, request, pk):
        obj = Ad.objects.get(id=pk)
        serializer = AdSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        obj = Ad.objects.get(id=pk)
        serializer = AdSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = Ad.objects.get(id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdSearchView(APIView, StandardResultsSetPagination):
    serializer_class = AdSerializer

    @extend_schema(
        summary="جستجوی آگهی‌ها",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='کلمه مورد نظر برای جستجو در عنوان و توضیحات آگهی',
                required=False,  # اختیاری
            ),
        ],
        responses={200: AdSerializer(many=True)}
    )

    def get(self, request):
        q = request.GET.get('q')
        queryset = Ad.objects.filter(Q(title=q) | Q(caption=q))
        page = self.paginate_queryset(queryset, request)
        serializer = AdSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)