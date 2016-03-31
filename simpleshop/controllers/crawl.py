import json
import requests
import bs4


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

    # Search query and get product id
    search_url = 'http://www.coupang.com/np/search?q=%s'
    try:
        search_page = requests.get(search_url % query)
        soup = bs4.BeautifulSoup(search_page.text)
        product_data_json = soup.find('ul', id='productList')['data-products']
        product_data = json.loads(product_data_json)

        product_id = product_data['indexes'][reroll]  # Get reroll-th product
    except:
        print("Can't get product id")
        raise

    # Try to parse all data from product page
    product_url = 'http://www.coupang.com/np/products/%d'
    try:
        product_page = requests.get(product_url % product_id)
        soup = bs4.BeautifulSoup(product_page.text)
        product_name = soup.find('span', 'product-name').text
        product_price = soup.find('strong', 'price').text
        product_image_url = soup.find('div', id='image0').img['src']
        product = {
            'id': product_id,
            'name': product_name,
            'price': product_price,
            'image': product_image_url
        }
        return product
    except:
        print('Failed to crawl data in the product page')

    # If parsing from product page fails, try to crawl xhr pages
    # Get product name and first item id
    basic_info_url = 'http://www.coupang.com/vp/products/%d/basic-info'
    try:
        basic_info_page = requests.get(basic_info_url % product_id)
        soup = bs4.BeautifulSoup(basic_info_page.text)
        product_name = soup.find('h2', 'prod-buy-header__title').text
        item_data_json = soup.find('div', 'detail-section')['data-reference']
        item_id = json.loads(item_data_json)['vendorItemId']
    except:
        print("Can't get basic info")
        raise

    # Get item price
    sales_info_url = 'http://www.coupang.com/vp/products/{product_id}/vendor-items/{item_id}/sale-infos'
    try:
        sales_info_page = requests.get(sales_info_url.format(product_id=product_id, item_id=item_id))
        soup = bs4.BeautifulSoup(sales_info_page.text)
        item_price = soup.find('span', id='totalPrice').text
    except:
        print("Can't get sales info")
        raise

    # Get item image
    product_image_url = 'http://www.coupang.com/vp/products/{product_id}/vendor-items/{item_id}/images'
    try:
        product_image_url.format(item_id=item_id, product_id=product_id)
        product_image_page = requests.get(product_image_url.format(item_id=item_id, product_id=product_id))
        soup = bs4.BeautifulSoup(product_image_page.text)
        item_image_url = soup.find('div', 'prod-image__item')['data-detail-img-src']
    except:
        print("Can't get image url")
        raise

    product = {
        'id': product_id,
        'name': product_name,
        'item_id': item_id,
        'price': item_price,
        'image': item_image_url
    }
    return product
