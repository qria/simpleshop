from flask import Blueprint, session, render_template, flash, request, redirect, url_for

from simpleshop.extensions import cache
from simpleshop.controllers.crawl import crawl_product_data
main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    """ Main page """
    cart_item = session.get('cart', [])
    cart_item_count = len(cart_item)
    return render_template('index.html', **locals())


def manage_cart(product, add=True, session=session):
    """ Add and remove products from cart.
        Cart is currently saved in session.
        Raises Exception when trying to add a existing product or remove a nonexistent one.
    """
    if add:
        # Add product to cart
        if product['id'] in [item['id'] for item in session['cart']]:
            raise Exception('이미 장바구니에 담긴 상품입니다.')

        session['cart'].append(product)
    else:
        # Remove product from cart
        for i, item in enumerate(session['cart']):
            if product['id'] == item['id']:
                session['cart'].pop(i)
                break
        else:
            raise Exception('장바구니에 해당 상품이 없습니다.')


@main.route('/search', methods=("GET", "POST"))
@main.route('/search/<query>', methods=("GET", "POST"))
def search(query=None):
    """ Search result page
    query: Query string
    reroll: How many times the user has pushed 'reroll' button
    """
    cart_item = session.get('cart', [])
    cart_item_count = len(cart_item)

    if request.method == 'POST':
        query = request.form['query']
        return redirect(url_for('main.search', query=query))

    reroll = request.args.get('reroll', type=int, default=0)
    try:
        product = crawl_product_data(query, reroll=reroll)
    except:
        product = None

    is_item_in_cart = product['id'] in [item['id'] for item in cart_item]
    add_to_cart = request.args.get('add_to_cart', type=bool, default=False)
    delete_from_cart = request.args.get('delete_from_cart', type=bool, default=False)
    if add_to_cart:
        try:
            manage_cart(product, add=True)
            flash('장바구니에 물건이 담겼습니다.')
        except Exception as e:
            flash(str(e))
        finally:
            cart_item = session['cart']
            cart_item_count = len(cart_item)
            is_item_in_cart = product['id'] in [item['id'] for item in cart_item]

    elif delete_from_cart:
        try:
            manage_cart(product, add=False)
            flash('장바구니에서 물건이 제거되었습니다.')
        except Exception as e:
            flash(str(e))
        finally:
            cart_item = session['cart']
            cart_item_count = len(cart_item)
            is_item_in_cart = product['id'] in [item['id'] for item in cart_item]

    return render_template('search.html', **locals())


@main.route('/cart')
def cart():
    cart_item = session.get('cart', [])
    cart_item_count = len(cart_item)
    return render_template('cart.html', **locals())
