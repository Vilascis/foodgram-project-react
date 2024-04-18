from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.api.pagination import CustomPaginator
from core.api.serializers import (
    FollowSerializer,
    RegisterSerializer,
    SetPasswordSerializer,
    UserSerializer,
)
from core.users.models import Subscribe, User


class UserViewSet(viewsets.ModelViewSet):
    """Регистрация пользователи и получение всех пользователеей."""

    allowed_methods = ('GET', 'POST', 'DELETE')
    lookup_field = 'public_id'
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator
    filter_backends = (SearchFilter,)
    search_fields = ('=username', '=public_id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return RegisterSerializer

    def partial_update(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=self.kwargs[self.lookup_field])
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def user_detail(self, request):
        """Получение своих данных."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
        url_path='set_password',
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        if user.check_password(self.request.data.get('current_password')):
            serializer = SetPasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response(
                    {'status': 'password set'}, status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, public_id):
        author = get_object_or_404(User, public_id=public_id)
        user = request.user
        subscription = Subscribe.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            if user == author:
                return Response(
                    {'error': 'Вы не можете подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):

        following = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
