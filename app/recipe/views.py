from core.models import Tag, Ingredient, Recipe, Image
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import TagSerializer, \
    IngredientSerializer, RecipeSerializer, RecipeDetailSerializer, ImageSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class AttributeModelViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).distinct().order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(AttributeModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(AttributeModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _get_ints_list_from_str(self, str_list, split_str=','):
        return [int(id_str) for id_str in str_list.split(split_str)]

    def filter_queryset_from_GET_parameter(self, queryset, param_name):
        filter_str = self.request.query_params.get(param_name)
        if filter_str:
            filter_list = self._get_ints_list_from_str(filter_str)
            queryset = queryset.filter(**{f'{param_name}__id__in': filter_list})
        return queryset

    def get_queryset(self):
        queryset = self.queryset
        queryset = self.filter_queryset_from_GET_parameter(queryset, 'tags')
        queryset = self.filter_queryset_from_GET_parameter(queryset, 'ingredients')
        return queryset.filter(user=self.request.user).distinct('id').order_by('-id')

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        return self.serializer_class


class ImageViewSet(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
