from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe


class AttributeModelSerializer(serializers.ModelSerializer):

    def __init__(self, class_model, **kwargs):
        super().__init__(**kwargs)

        class Meta:
            model = class_model
            fields = ('id', 'name')
            read_only_fields = ('id',)

        self.Meta = Meta


class TagSerializer(AttributeModelSerializer):

    # TODO remove the "*args" parameter.
    def __init__(self, *args, **kwargs):
        super().__init__(Tag, **kwargs)


class IngredientSerializer(AttributeModelSerializer):

    # TODO remove the "*args" parameter.
    def __init__(self, *args, **kwargs):
        super().__init__(Ingredient, **kwargs)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'minutes_required', 'price',
            'link', 'ingredients', 'tags'
        )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
