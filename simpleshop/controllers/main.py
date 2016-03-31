from flask import Blueprint, render_template, flash, request, redirect, url_for

from simpleshop.extensions import cache
from simpleshop.controllers.crawl import crawl_product_data
main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    """ Main page """
    return render_template('index.html')


@main.route('/search', methods=("GET", "POST"))
@main.route('/search/<query>', methods=("GET", "POST"))
def search(query=None):
    """ Search result page
    query: Query string
    reroll: How many times the user has pushed 'reroll' button
    """
    if request.method == 'POST':
        query = request.form['query']
        return redirect(url_for('main.search', query=query))

    reroll = request.args.get('reroll', type=int, default=0)
    try:
        product = crawl_product_data(query, reroll=reroll)
    except:
        product = None

    return render_template('search.html', **locals())
