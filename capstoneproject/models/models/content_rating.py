from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, ManyToManyField, \
    DateTimeField, Manager, CASCADE
from capstoneproject.models.models.content import Content
from capstoneproject.models.models.category_rating import CategoryRating
from capstoneproject.models.models.word_count import WordCount
from capstoneproject.models.models.category import Category
from capstoneproject.models.models.word import Word
from capstoneproject.models.fields.rating_field import RatingField


class ContentRating(Model):
    """
    This Model contains data related to one rated content,
    its overall rating, category ratings, word counts,
    and created and updated dates.
    """
    content = ForeignKey(Content, on_delete=CASCADE)
    rating = RatingField(default=0)
    category_ratings = ManyToManyField(
        CategoryRating,
        related_name='content_ratings')
    word_counts = ManyToManyField(WordCount, related_name='content_ratings')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    content_ratings = Manager()

    class Meta:
        default_manager_name = 'content_ratings'

    def __str__(self):
        string = 'Rating\n'
        string += '  Overall Rating: {}\n'.format(self.rating)
        string += '  Category Ratings: {}\n'.format(self.category_ratings)
        string += '  Word Counts: {}\n'.format(self.word_counts)
        string += '  Created: {}    Updated: {}\n'. format(self.created, self.updated)
        return string

    def get_category_ratings(self):
        category_ratings = dict()
        for cat_rating in self.category_ratings.all():
            category_ratings[cat_rating.category.name] = cat_rating.rating
        return category_ratings

    def _create_word_count_dict(self):
        word_counts = dict()
        for wc in self.word_counts.all():
            word_counts[wc.word.name] = wc.count
        return word_counts

    def get_word_count_category(self):
        word_count_category_dict = dict()  # Initialize the dictionary.
        for cat in Category.categories.all():  # Add a key for each category.
            word_count_category_dict[cat.name] = dict()

        word_count_dict = self._create_word_count_dict()
        for word, count in word_count_dict.items():
            word_model = Word.words.get_word(word=word)  # Get Word model
            for word_cat in word_model.get_categories():  # For each category.
                word_count_category_dict[word_cat][word] = count
        return word_count_category_dict