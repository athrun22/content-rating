"""
This file contains functions that provide help create the information displayed in the various views.
"""
import os
import capstoneproject.content_rating.algorithm.text as text
from capstoneproject.shared import rater
from capstoneproject import parsing
from django.contrib.auth.models import User
from capstoneproject.app_forms import CopyInForm, SongSearchForm, WebsiteSearchForm, UploadFileForm

from capstoneproject.helpers import model_helper


def perform_rating(content: str, form, request):
    """
    This function coordinates the ratings of textual content and returns a dictionary containing
    the rating results.
    :param content: A string, the content to rate
    :param form: A form submitted by the user, contains information about the content.
    :param request: The HTML request.
    :return: A dictionary containing the rating results.
    """
    rated_content = get_rating_results(content, form)  # Get the rating's results
    model_helper.update_user_ratings(rated_content, request.user)  # Save the rating
    context = generate_context(rated_content, 'current')  # Generate the context

    return context


def get_rating_results(content: str, form):
    """
    This function classifies and rates the given text.
    It then saves the rating information.
    Lastly, it returns a dictionary containing the rating results.
    :param content: A string, the content to rate.
    :param form: A form, submitted by the user and contains information about the content.
    :return: A dictionary containing the rating results
    """
    # TODO handle overall rating of 0
    rated_content = rater.algorithm(content)  # Perform algorithm
    rated_content.title = form.get_title()  # Set the rated content's title
    rated_content.creator = form.get_creator()  # Set the rated content's creator
    rated_content.content_type = get_content_type(form)  # Set the content type
    return rated_content


def get_content_type(form):
    """
    This function returns the content type of the content being rated.
    :param form: The form containing details about the rated content.
    :return: The content type as a string
    """
    content_type = 4
    if isinstance(form, CopyInForm):
        content_type = 4  # 'document'
    elif isinstance(form, SongSearchForm):
        content_type = 0  # 'song'
    elif isinstance(form, WebsiteSearchForm):
        content_type = 3  # 'website'
    elif isinstance(form, UploadFileForm):
        content_type = 4  # 'document'
    return content_type


def generate_context(rated_content: text.Text, name: str):
    """
    Generates a dictionary that contains key information from a rated text.
    :param rated_content: The rated text used to create the dictionary.
    :param name: A string to add to the start of every field in the context.
    :return: A dictionary, containing the rated text's information.
    """
    context = {'{}_name'.format(name): rated_content.title,
               '{}_creator'.format(name): rated_content.creator,
               '{}_overall_rating'.format(name): int(rated_content.overall_rating),
               '{}_category_ratings'.format(name): rated_content.category_ratings,
               '{}_category_word_counts'.format(name): rated_content.category_word_counts
               }
    return context


def get_file_content(file):
    """
    This function coordinates the collection of text from a file.
    It firsts unloads the file which is originally from the HTML request into a temp file.
    Then it parses the temp file to obtain its text.
    Then it deletes the temp file.
    Lastly it returns the file's text.
    :param file: A file.
    :return: A string, the file's text.
    """
    chunk_uploaded_file(file)  # Transfer file from HTML Request
    file_text = parse_file(file.name)  # Get text from temp file
    os.remove('capstoneproject/tempfile')  # Delete the temp file after use
    return file_text


def chunk_uploaded_file(f):
    """
    This function reads the given file in chunks and writes the file to another file.
    :param f: The file to read.
    :return: None.
    """
    with open('capstoneproject/tempfile', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def parse_file(file_name):
    """
    This function parses the contents of a temporary file based on the type of the file.
    :param file_name: A string, the file name.
    :return: A string, the contents of the file.
    """
    if file_name.endswith('.pdf'):
        file_text = parsing.parse_pdf('capstoneproject/tempfile')
    elif file_name.endswith('.epub'):
        file_text = parsing.parse_epub('capstoneproject/tempfile')
    elif file_name.endswith('docx'):
        file_text = parsing.parse_docx('capstoneproject/tempfile')
    elif file_name.endswith('txt'):
        file_text = parsing.parse_txt('capstoneproject/tempfile')
    else:
        print('ERROR')  # TODO Handle this error
        file_text = ''
    return file_text


def create_category_ratings_dict(category_ratings_queryset):
    category_ratings = dict()
    for query in category_ratings_queryset:
        category_ratings[query.category.name] = query.rating
    return category_ratings


def create_word_count_dict(word_count_queryset):
    word_count = dict()
    for query in word_count_queryset:
        word_count[query.word.name] = query.count
    return word_count


def create_word_count_category_dict(word_count_dict: dict):
    word_count_category_dict = dict()  # Initialize the dictionary.
    for cat in model_helper.get_categories():  # Add a key for each category.
        word_count_category_dict[cat.name] = dict()

    for word, count in word_count_dict.items():
        word_model = model_helper.get_word(word)
        for word_cat in word_model.get_categories():  # each category.
            word_count_category_dict[word_cat][word] = count
    return word_count_category_dict


def get_rating(user: User, pos: int):
    """
    This function creates a Text object from the User's most recent Rating.
    :param user: A User
    :param pos: the position to retrieve in the list of the user's ratings.
    :return: A Text object containing the data from the User's most recent Rating
    """
    rating = model_helper.get_user_rating_at_position(user, pos)
    if not rating:
        return None
    rated_text = text.Text([])
    rated_text.title = rating.content.title
    rated_text.creator = rating.content.creator
    rated_text.overall_rating = rating.rating
    rated_text.category_word_counts = rating.get_word_count_category()
    rated_text.category_ratings = rating.get_category_ratings()

    return rated_text


def get_word_counts_context(user: User, pos: int):
    """
    This function creates the context dictionary to pass to the
    word counts page. The dictionary contains keys for the content
    title and for the category word counts dictionary.
    :param user: A User
    :param pos: An int, the position in the user's past rated
    content ordered where the most recent are at the top to
    retrieve word counts for
    :return: A dictionary
    """
    context = {'name': '',
               'category_word_counts': dict()
               }
    rating = model_helper.get_user_rating_at_position(user, pos)
    if not rating:
        return context
    context['name'] = rating.content.title
    context['category_word_counts'] = rating.get_word_count_category()
    return context
