from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient, Image
from recipe.serializers import RecipeSerializer,\
    RecipeDetailSerializer, TagSerializer, IngredientSerializer, ImageSerializer


RECIPE_URL = reverse('recipe:recipe-list')


class UnauthorizedRecipeTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        response = self.client.get(RECIPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedRecipeTests(TestCase):

    def create_user(self, email='hello@heelo.com', password='hoLLa@123'):
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        return user

    def get_recipe_payload(self, **kwargs):
        args = {
            'user': self.user,
            'title': 'abc',
            'minutes_required': 5,
            'price': 5.00
        }
        args.update(kwargs)
        return args

    def create_recipe(self, **kwargs):
        args = self.get_recipe_payload(**kwargs)
        return Recipe.objects.create(**args)

    def create_attribute(self, attr, user=None, **kwargs):
        if user is None:
            user = self.user
        return attr.objects.create(user=user, **kwargs)

    def create_tag(self, name='xyz', user=None):
        return self.create_attribute(Tag, name=name, user=user)

    def create_ingredient(self, name='xyz', user=None):
        return self.create_attribute(Ingredient, name=name, user=user)

    def create_image(self, user=None, image='./images/1.jpg', **kwargs):
        if user is None:
            user = self.user
        return Image.objects.create(user=user, image=image, **kwargs)

    def assertRecipeDictEqual(self, recipe, dictionary):
        for key in dictionary:
            self.assertEqual(dictionary[key], getattr(recipe, key))

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(email='hoo@hee.com')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        self.create_recipe()
        self.create_recipe()
        recipes = Recipe.objects.all().order_by('-id')

        response = self.client.get(RECIPE_URL)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_user_can_see_only_its_recipes(self):
        other_user = self.create_user()
        self.create_recipe(user=other_user)
        self.create_recipe()
        self.create_recipe()

        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, serializer.data)

    def get_detail_url(self, id):
        return reverse('recipe:recipe-detail', args=[id])

    def test_recipe_view_detail(self):
        recipe = self.create_recipe()
        recipe.tags.add(self.create_tag())
        recipe.ingredients.add(self.create_ingredient())

        serializer = RecipeDetailSerializer(recipe)

        url = self.get_detail_url(recipe.id)
        response = self.client.get(url)

        self.assertEqual(serializer.data, response.data)

    def get_recipe_from_response(self, response):
        return Recipe.objects.get(id=response.data['id'])

    def test_create_invalid_recipe(self):
        payload = {'user': -1}
        response = self.client.post(RECIPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_valid_recipe(self):
        payload = self.get_recipe_payload()
        response = self.client.post(RECIPE_URL, payload)
        recipe = self.get_recipe_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertRecipeDictEqual(recipe, payload)

    def assertAttrIDsInRecipe(self, serializer, list_name, *args):
        args_list = list(x.id for x in args)
        kwargs = {list_name: args_list}
        payload = self.get_recipe_payload(**kwargs)
        response = self.client.post(RECIPE_URL, payload)
        recipe = self.get_recipe_from_response(response)
        recipe_data = serializer(getattr(recipe, list_name), many=True).data
        response_data = response.data[list_name]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for x in recipe_data:
            self.assertIn(x['id'], response_data)

    def test_recipe_tags_are_present(self):
        tag1 = self.create_tag(name='abc')
        tag2 = self.create_tag(name='def')
        self.assertAttrIDsInRecipe(TagSerializer, 'tags', tag1, tag2)

    def test_recipe_ingredients_are_present(self):
        ingredient1 = self.create_ingredient(name='abc')
        ingredient2 = self.create_ingredient(name='def')
        self.assertAttrIDsInRecipe(IngredientSerializer, 'ingredients', ingredient1, ingredient2)

    def test_recipe_images_are_present(self):
        image1 = self.create_image()
        image2 = self.create_image()
        self.assertAttrIDsInRecipe(ImageSerializer, 'images', image1, image2)

    def test_recipe_put_request(self):
        recipe = self.create_recipe()
        recipe.tags.add(self.create_tag())
        payload = self.get_recipe_payload(title='hohoho')

        self.client.put(self.get_detail_url(recipe.id), payload)
        recipe.refresh_from_db()

        self.assertEqual(len(recipe.tags.all()), 0)
        self.assertEqual(recipe.title, payload['title'])

    def test_recipe_patch_request(self):
        recipe = self.create_recipe()
        recipe.tags.add(self.create_tag())
        payload = self.get_recipe_payload(title='hohoho')

        self.client.patch(self.get_detail_url(recipe.id), payload)
        recipe.refresh_from_db()

        self.assertEqual(len(recipe.tags.all()), 1)
        self.assertEqual(recipe.title, payload['title'])

    def create_recipe_with_given_attributes(self, create_func, field_name, attr_name):
        payload = self.get_recipe_payload()
        recipe = self.create_recipe(**payload)
        attr = create_func(name=attr_name)
        getattr(recipe, field_name).add(attr)
        return [recipe, attr]

    def create_recipe_with_a_tag(self, tag_name):
        return self.create_recipe_with_given_attributes(
            self.create_tag,
            'tags',
            tag_name
        )

    def create_recipe_with_an_ingredient(self, ingredient_name):
        return self.create_recipe_with_given_attributes(
            self.create_ingredient,
            'ingredients',
            ingredient_name
        )

    def assert_filter_recipes_by_attributes(self, create_func, field_name):
        recipe1, attr1 = create_func('a')
        recipe2, attr2 = create_func('b')
        recipe3, attr3 = create_func('c')

        response = self.client.get(RECIPE_URL, {field_name: f'{attr1.id},{attr2.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def assert_filter_recipes_are_distinct(self, attr_create_func, field_name):
        attr1 = attr_create_func(name='a')
        attr2 = attr_create_func(name='b')
        recipe = self.create_recipe()
        getattr(recipe, field_name).add(attr1)
        getattr(recipe, field_name).add(attr2)

        response = self.client.get(RECIPE_URL, {field_name: f'{attr1.id},{attr2.id}'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_recipes_by_tags(self):
        self.assert_filter_recipes_by_attributes(
            self.create_recipe_with_a_tag,
            'tags'
        )

    def test_filter_recipes_by_ingredients(self):
        self.assert_filter_recipes_by_attributes(
            self.create_recipe_with_an_ingredient,
            'ingredients'
        )

    def test_filter_recipes_by_tags_are_distinct(self):
        self.assert_filter_recipes_are_distinct(
            self.create_tag,
            'tags'
        )

    def test_filter_recipes_by_ingredients_are_distinct(self):
        self.assert_filter_recipes_are_distinct(
            self.create_ingredient,
            'ingredients'
        )
