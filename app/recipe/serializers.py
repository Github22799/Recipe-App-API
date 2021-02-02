from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe, Image


class AttributeModelSerializer(serializers.ModelSerializer):

    def __init__(self, class_model, **kwargs):
        super().__init__(**kwargs)

        class Meta:
            model = class_model
            fields = ('id', 'name')
            read_only_fields = ('id',)

        self.Meta = Meta


class ImageSerializer(serializers.ModelSerializer):
    # TODO you might change it to True later.
    image = serializers.ImageField(use_url=False)

    class Meta:
        model = Image
        fields = ('id', 'image', 'description')
        read_only_fields = ('id', )


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
            'id', 'title', 'images', 'minutes_required', 'price',
            'link', 'ingredients', 'tags'
        )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    images = ImageSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
