import webbrowser
import requests
import bs4
import urllib2
import util

# webbrowser.open('https://secure.newegg.com/Shopping/AddToCart.aspx?Submit=ADD&ItemList=9SIA6V66R23609')
# # webbrowser.open('https://secure.newegg.com/Shopping/ShoppingCart.aspx?submit=ChangeItem')

# webbrowser.open('https://secure.newegg.com/GlobalShopping/CheckoutStep1.aspx?CartID=260%2bNADFRMO5ORIRJB8&IsFromCart=1&SkippedSignIn=1')

class Newegg:

    def __init__(self, item_id):
        self.item_id = item_id
        self.add_to_cart()

    def add_to_cart(self):
        url = 'https://secure.newegg.com/Shopping/AddToCart.aspx?Submit=ADD&ItemList=' + str(self.item_id)
        util.print_header("Visiting:", url)
        webbrowser.open(url)
