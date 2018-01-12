import requests
from constants import *
import secret


def get_account_ids(customer_id):
    get_params = {"key": secret.NESSIE_KEY}
    get_request = requests.get("{}/customers/{}/accounts".format(API_ROOT, customer_id), params=get_params)
    return [account["_id"] for account in get_request.json()]

def get_all_purchases(customer_id):
    purchases = []
    for account_id in get_account_ids(customer_id):
        get_params = {"key": secret.NESSIE_KEY}
        get_request = requests.get("{}/accounts/{}/purchases".format(API_ROOT, account_id), params=get_params)
        purchases.extend(
                {"merchant_id": purchase["merchant_id"],
                    "purchase_date": purchase["purchase_date"],
                    "amount": purchase["amount"],
                    }
                for purchase in get_request.json() if purchase["type"] == "merchant")
    return purchases

def get_merchant_categories(merchant_id):
    get_params = {"key": secret.NESSIE_KEY}
    get_request = requests.get("{}/merchants/{}".format(API_ROOT, merchant_id), params=get_params)
    return get_request.json()["category"]

def get_merchant_data(merchant_id):
    get_params = {"key": secret.NESSIE_KEY}
    get_request = requests.get("{}/merchants/{}".format(API_ROOT, merchant_id), params=get_params)
    the_json = get_request.json()
    return {"category": the_json["category"], "geocode": the_json["geocode"]}


def get_general_category(categories):
    """
    Returns a general category given an array of Google categories.
    """
    for general_category in GENERAL_CATEGORIES:
        if any(category in GENERAL_CATEGORIES[general_category] for category in categories):
            return general_category
    return "other"

def categorize_purchases(purchases):
    categorized_purchases = {category: [] for category in GENERAL_CATEGORIES.keys()}
    categorized_purchases["other"] = []

    for purchase in purchases:
        purchase_general_category = get_general_category(get_merchant_categories(purchase["merchant_id"]))
        purchase_data = get_merchant_data(purchase["merchant_id"])
        purchase_data["purchase_date"] = purchase["purchase_date"]
        purchase_data["purchase_category"] = purchase_general_category
        categorized_purchases[purchase_general_category].append(purchase_data)

    return categorized_purchases

def sort_purchases_by_date(categorized_purchases):
    all_purchases = []
    for category in categorized_purchases.keys():
        all_purchases.extend(categorized_purchases[category])
    all_purchases.sort(key=lambda p: p["purchase_date"])

    return all_purchases

def get_sorted_filtered_purchases(customer_id):
    return sort_purchases_by_date(categorize_purchases(get_all_purchases(customer_id)))

if __name__ == "__main__":
    print(get_sorted_filtered_purchases(CUSTOMER_ID))
