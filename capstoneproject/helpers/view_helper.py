"""
This file contains functions that provide help create the information displayed in the various views.
"""
import os
import capstoneproject.content_rating.algorithm.text as text
import capstoneproject.app_forms.forms as forms
from capstoneproject.shared import rater
from capstoneproject import parsing
from capstoneproject.helpers import model_helper


def perform_rating(content: str, form, request):
    """
    This function coordinates the ratings of textual content.
    :param content: A string, the content to rate
    :param form: A form submitted by the user, contains information about the content.
    :param request: The HTML request.
    :return: A dictionary containing the rating results.
    """
    context = get_rating_results(content, form, request.user)
    request.session['category_words'] = context['category_word_counts']
    return context


def get_rating_results(content: str, form, user):
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

    model_helper.save_rating(rated_content, user)  # Save the user's rating

    return generate_context(rated_content)


def get_content_type(form):
    """
    This function returns the content type of the content being rated.
    :param form: The form containing details about the rated content.
    :return: The content type as a string
    """
    content_type = 4
    if isinstance(form, forms.copy_in_form.CopyInForm):
        content_type = 4  # 'document'
    elif isinstance(form, forms.song_search_form.SongSearchForm):
        content_type = 0  # 'song'
    elif isinstance(form, forms.webpage_search_form.WebsiteSearchForm):
        content_type = 3  # 'website'
    elif isinstance(form, forms.upload_file_form.UploadFileForm):
        content_type = 4  # 'document'

    return content_type


def generate_context(rated_content: text.Text):
    """
    Generates a dictionary that contains key information from a rated text.
    :param rated_content: The rated text used to create the dictionary.
    :return: A dictionary, containing the rated text's information.
    """
    context = {'name': rated_content.title,
               'creator': rated_content.creator,
               'overall_rating': int(rated_content.overall_rating),
               'category_ratings': rated_content.category_ratings,
               'category_word_counts': rated_content.category_word_counts
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
    handle_uploaded_file(file)  # Transfer file from HTML Request
    file_text = parse_file(file.name)  # Get text from temp file
    # print(text)
    os.remove('capstoneproject/tempfile')  # Delete the temp file after use
    return file_text


def handle_uploaded_file(f):
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
