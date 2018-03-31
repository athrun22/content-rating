"""
This file contains functions that will correspond with the HTML pages for the
web application. Each HTML page will call a function which will provide the
site's functionality.
"""
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf

from capstoneproject.display import display_categories, display_words, display_category_words
from capstoneproject.forms import SignUpForm, LoginForm
from capstoneproject.content_rating.algorithm import content_rating
from capstoneproject.models import Weight


def login(request):
    """
    This function handles HTML requests from the Login page.
    :param request: The HTML request containing the user's action.
    :return: Renders the proper HTML page depending on the user's actions.
    """
    if request.method == 'POST':
        if request.POST.get('submit') == 'signup':
            form = SignUpForm(request.POST)
            if form.is_valid():  # Check if the form is valid.
                form.save()
                # Obtain the username and password from the valid form.
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                # Authenticate and login the user.
                user = authenticate(username=username, password=raw_password)
                auth_login(request, user)
                # Go to the home screen if the user is now authenticated and
                # logged in.
                return render(request, 'homepage.html')
            else:  # Go back to the login in page with a new login form if the
                return render(request, 'login.html',
                              {'login_form': LoginForm(), 'signup_form': form})

        if request.POST.get('submit') == 'login':
            form = LoginForm(request.POST)
            if form.is_valid():  # Check if the form is valid.
                login_username = form.cleaned_data.get('login_username')
                raw_password = form.cleaned_data.get('login_password')
                user = authenticate(
                    username=login_username,
                    password=raw_password)
                if user is not None:
                    if user.is_active:
                        auth_login(request, user)
                        return redirect('homepage')
                    else:
                        login_form = LoginForm()
                        login_form.disabled_account_error()
                        return render(request, 'login.html',
                                      {'login_form': form,
                                       'signup_form': SignUpForm()})
            # If the form is not valid, return to the login page.
            return render(request, 'login.html',
                          {'login_form': LoginForm(),
                           'signup_form': SignUpForm()})
    else:
        c = {}
        c.update((csrf(request)))
        c.update(({'login_form': LoginForm(), 'signup_form': SignUpForm()}))
        return render_to_response('login.html', c)


def login_redirect(request):
    """
    Function to handle login redirection.
    :param request: The HTML request to handle.
    :return: A redirection to the login page.
    """
    return redirect('login')


@login_required(login_url='/login/')
def homepage(request):
    """
    Function to handle requests on the home page.
    :param request: The HTML request to handle.
    :return: Renders the home page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    if request.method == "POST":
        request.session['content_compare'] = request.POST['content_compare']
    return render(request, 'homepage.html')


def logout(request):
    """
    Function to handle log out requests.
    :param request: The HTML request to handle.
    :return: Renders the login page after logging the user out.
    """
    logout(request)
    return render(request, 'login.html',
                  {'login_form': LoginForm, 'signup_form': SignUpForm})


@login_required(login_url='/login/')
def profile(request):
    """
    Function to handle requests on the profile page.
    :param request: The HTML request to handle.
    :return: Renders the profile page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    weight_dict = dict()
    for weight in Weight.WEIGHTS:
        weight_dict[weight[0]] = weight[1]
    recently_rated = {'Pillow Talkin': 9,
                      'Baby Got Back': 7,
                      'Africa': 1,
                      'Freebird': 5,
                      'My First Song': 3
                      }
    context = {'categories': display_categories(),
               'recently_rated': recently_rated,
               'weight_levels': len(weight_dict) - 1,
               'weight_dict': weight_dict
               }
    return render(request, 'profile.html', context)


@login_required(login_url='/login/')
def search(request):
    """
    Function to handle requests to search for entertainment content from web
        sources.
    :param request: The HTML request to handle.
    :return: Renders the search page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    # cr = content_rating.ContentRating()
    # cr.algorithm('')
    return render(request, 'search.html')


@login_required(login_url='/login/')
def upload(request):
    """
    Function to handle requests to upload files to rate.
    :param request: The HTML request to handle.
    :return: Renders the upload page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    return render(request, 'upload.html')


@login_required(login_url='/login/')
def copy_in(request):
    """
    Function to handle requests to copy text in to rate.
    :param request: The HTML request to handle.
    :return: Renders the copy-in page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    return render(request, 'copy-in.html')


def about_algorithm(request):
    """
    Function to handle requests on the about algorithm homepage.
    :param request: The HTML request to handle.
    :return: Renders the about algorithm page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    return render(request, 'algorithm.html')


def about_page(request):
    """
    Function to handle requests on the about us page.
    :param request: The HTML request to handle.
    :return: Renders the about us algorithm page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    return render(request, 'about.html')


@login_required(login_url='/login/')
def words(request, category):
    """
    Function to handle requests on the page containing the offensive words and
        their levels of offensiveness.
    :param request: The HTML request to handle.
    :return: Renders the words page.
    """
    if request.session.get('delete'):
        del request.session['delete']
        del request.session['content_compare']
    weight_dict = dict()
    for weight in Weight.WEIGHTS:
        weight_dict[weight[0]] = weight[1]
    context = {'category': category,
               'words': display_category_words(category),
               'weight_levels': len(weight_dict) - 1,
               'weight_dict': weight_dict
               }
    return render(request, 'words.html', context)


@login_required(login_url='/login/')
def rating_results(request):
    """
    Function to handle requests on the rating results page.
    :param request: The HTML request to handle.
    :return: Renders the rating results page.
    """
    if 'content_compare' in request.session:
        return redirect('compare')
    category_ratings = dict()
    category_word_counts = dict()
    for category in display_categories():
        category_ratings[category.name] = 5
        category_word_counts[category.name] = {'word1': 4,
                                               'word2': 3,
                                               'word3': 2
                                               }
    context = {'name': 'Pillow Talkin',
               'creator': "Lil' Dicky (feat. BRAIN)",
               'overall_rating': 7,
               'category_ratings': category_ratings,
               'category_word_counts': category_word_counts
               }
    return render(request, 'rating-result.html', context)


@login_required(login_url='/login/')
def compare_results(request):
    """
    Function to handle requests to compare rating results.
    :param request: The HTML request to handle.
    :return: Renders the compare page.
    """
    content_compare = request.session['content_compare']  # name of item to be compared, will be Content object in future
    request.session['delete'] = True
    current_category_ratings = dict()
    current_category_word_counts = dict()
    previous_category_ratings = dict()
    previous_category_word_counts = dict()
    for category in display_categories():
        current_category_ratings[category.name] = 5
        previous_category_ratings[category.name] = 8
        current_category_word_counts[category.name] = {'word1': 4,
                                                       'word2': 3,
                                                       'word3': 2
                                                       }
        previous_category_word_counts[category.name] = {'word1': 7,
                                                        'word2': 4,
                                                        'word3': 6
                                                        }
    context = {'current_name': 'Baby Got Back',
               'current_creator': 'Sir Mix a Lot',
               'previous_name': content_compare,
               'previous_creator': "Lil' Dicky (feat. BRAIN)",
               'current_overall_rating': 7,
               'previous_overall_rating': 5,
               'current_category_ratings': current_category_ratings,
               'current_category_word_counts': current_category_word_counts,
               'previous_category_ratings': previous_category_ratings,
               'previous_category_word_counts': previous_category_word_counts
               }
    return render(request, 'compare.html', context)


@login_required(login_url='/login/')
def word_counts(request, name):
    """
    Function to handle requests to the word counts page.
    :param request: The HTML request to handle.
    :return: Renders the word-counts page.
    """
    category_word_counts = dict()
    for category in display_categories():
        category_word_counts[category.name] = {'word1': 4,
                                               'word2': 3,
                                               'word3': 2
                                               }
    context = {'name': name,
               'category_word_counts': category_word_counts
               }
    return render(request, 'word-counts.html', context)
