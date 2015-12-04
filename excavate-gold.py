import requests

from random import randint
from time import sleep

url = "https://resilient-integration-workshop.herokuapp.com"
register = "/v1/register?userName=%s"
excavate = "/v1/excavate"
store = "/v1/store?userId=%s&bucketId=%s"
totals = "/v1/totals?userId=%s"


def retry_request(request_type, url):
    success = False
    timeout = 1
    while not success:
        try:
            result = getattr(requests, request_type)(url, timeout=timeout)
        except requests.exceptions.Timeout:
            sleep(1)
            timeout = timeout ** 2 if timeout != 1 else 2
            continue

        if result.status_code == 200:
            success = True

    return result


def process_excavate_respose(response):
    try:
        json = response.json()
        bucket_id = json.get('bucketId', '')
        gold = json.get('gold', {}).get('units', 0)
        return (bucket_id, gold)
    except:
        return ('', 0)


def get_username_and_user_id():
    user_id = ''
    while not user_id:
        username = "figarocorso_%d" % randint(10e6, 10e8)
        response = retry_request('post', url + register % username)
        try:
            user_id = response.json().get('user', '')
        except:
            user_id = ''

    return (username, user_id)


def store_gold_units(user_id, bucket_id):
    store_result = False
    while not store_result:
        response = retry_request('post', url + store % (user_id, bucket_id))
        store_result = response.json()


def print_gold_status(user_id):
    success = False
    while not success:
        result = retry_request('get', url + totals % user_id)
        try:
            gold_units = int(result.json().get('goldTotal', None))
            print "Current gold units excavated: %d" % gold_units
            success = True
        except:
            pass


if __name__ == "__main__":
    (username, user_id) = get_username_and_user_id()
    print "%s has the userId: %s" % (username, user_id)
    total_gold_units = 0
    # This should be a while True ^_^
    while total_gold_units < 1000:
        response = retry_request('post', url + excavate)
        (bucket_id, gold_units) = process_excavate_respose(response)
        if bucket_id and gold_units:
            total_gold_units += gold_units
            store_gold_units(user_id, bucket_id)
            print_gold_status(user_id)
