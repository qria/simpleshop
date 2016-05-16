import json
import bs4
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from simpleshop.controllers.measure_time import measure_time
from simpleshop.extensions import cache


@measure_time
@cache.memoize()
def crawl_product_data(query, reroll=None):
    """ Crawl product data from coupang with given query.
    Note that coupang has a lot of different formats for a product page,
    making it hard to parse it in a simple way.
    One format has all the information on product page
    and the other has them all scatter throughout xhr pages.
    It may be distinguishable from the scale of product_id (not sure yet).

    reroll: Chooses reroll-th product in the search results
        products that are not in first page aren't supproted yet.
        If no value is given, chooses the first product.

    Returns a dictionary with product data.
    """
    if not reroll:
        reroll = 0

    # Asynchronously crawl all necessary pages

    session = FuturesSession(executor=ThreadPoolExecutor(max_workers=10))

    search_url = 'http://www.coupang.com/np/search?q=%s' % query
    future_search_page = session.get(search_url)

    # Search query and get product id
    try:
        search_page = future_search_page.result()
        soup = bs4.BeautifulSoup(search_page.text)
        product_data_json = soup.find('ul', id='productList')['data-products']
        product_data = json.loads(product_data_json)

        # if adult product, reroll until it's not
        # TODO: implement login so we can view adult products
        while True:
            product_id = product_data['indexes'][reroll]  # Get reroll-th product
            if 'adultProduct' in soup.find('li', id=product_id).img['src']:
                    reroll += 1
            else:
                break
    except:
        print("Can't get product id")
        raise

    # Links with product_id needed is crawled after getting product_id

    product_url = 'http://www.coupang.com/np/products/%d' % product_id
    future_product_page = session.get(product_url)
    basic_info_url = 'http://www.coupang.com/vp/products/%d/basic-info' % product_id
    future_basic_info_page = session.get(basic_info_url)

    # Try to parse all data from product page
    try:
        product_page = future_product_page.result()
        soup = bs4.BeautifulSoup(product_page.text)
        product_name = soup.find('span', 'product-name').text
        product_price_raw = soup.find('strong', 'price').text
        product_price = int(product_price_raw.replace(',', ''))
        product_image_url = soup.find('div', id='image0').img['src']
        product = {
            'id': product_id,
            'url': product_url,
            'name': product_name,
            'price': product_price,
            'image': product_image_url
        }
        return product
    except:
        print('Failed to crawl data in the product page')

    # If parsing from product page fails, try to crawl xhr pages
    # Get product name and first item id
    try:
        basic_info_page = future_basic_info_page.result()
        soup = bs4.BeautifulSoup(basic_info_page.text)
        product_name = soup.find('h2', 'prod-buy-header__title').text
        item_data_json = soup.find('div', 'detail-section')['data-reference']
        item_id = json.loads(item_data_json)['vendorItemId']
    except:
        print("Can't get basic info")
        raise

    # Crawl pages with item_id here
    sales_info_url = 'http://www.coupang.com/vp/products/{product_id}/vendor-items/{item_id}/sale-infos'.format(product_id=product_id, item_id=item_id)
    future_sales_info_page = session.get(sales_info_url)
    product_image_url = 'http://www.coupang.com/vp/products/{product_id}/vendor-items/{item_id}/images'.format(item_id=item_id, product_id=product_id)
    future_product_image_page = session.get(product_image_url)

    # Get item price
    try:
        sales_info_page = future_sales_info_page.result()
        soup = bs4.BeautifulSoup(sales_info_page.text)
        item_price_raw = soup.find('span', id='totalPrice').text
        item_price = int(item_price_raw.replace(',', ''))
    except:
        print("Can't get sales info")
        raise

    # Get item image
    try:
        product_image_page = future_product_image_page.result()
        soup = bs4.BeautifulSoup(product_image_page.text)
        item_image_url = soup.find('div', 'prod-image__item')['data-detail-img-src']
    except:
        print("Can't get image url")
        raise

    product = {
        'id': product_id,
        'name': product_name,
        'url': product_url,
        'item_id': item_id,
        'price': item_price,
        'image': item_image_url
    }
    return product
