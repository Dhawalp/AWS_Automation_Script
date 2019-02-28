from django.shortcuts import render
from rest_framework import permissions, viewsets
from .permissions import IsOwnerOrReadOnly
from .models import Book
from .serializers import BookSerializer
# Create your views here.


class BookApiView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)




