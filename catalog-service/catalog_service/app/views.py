from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer


class CategoryListCreate(APIView):
    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(CategorySerializer(cat).data)

    def put(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategorySerializer(cat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cat = self.get_object(pk)
        if not cat:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
