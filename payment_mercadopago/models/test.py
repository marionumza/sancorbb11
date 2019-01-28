import mercadopago
import json

mp = mercadopago.MP("6165452150525723", "zKPu7O8TREbFfh4Fh87hi1SFjM1f1Rin")
accessToken = mp.get_access_token()
# print ("mp>>>>>>>>>", accessToken)

preference = {"items": [
    {"title": "sdk-python test_client_id_and_client_secret", "quantity": 1, "currency_id": "ARS", "unit_price": 10.5,
        "back_urls": {'pending': 'http://localhost:8888/shop/', 'success': 'http://localhost:8888/',
            'failure': 'http://localhost:8888/shop/'}, 'auto_return': 'approved'}]}


mpc = mp.create_preference(preference)

# print("test_client_id_and_client_secret OK!>>>>>", json.dumps(mpc, indent=4))
