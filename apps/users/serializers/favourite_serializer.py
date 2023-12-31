from rest_framework.serializers import ModelSerializer

from apps.users.models.favourite import Favourite
from apps.movies.serializers.movie_serializer import MovieSerializer


class FavouriteSerializer(ModelSerializer):
    movie = MovieSerializer()

    class Meta:
        model = Favourite
        fields = 'movie',
        # depth = 1
