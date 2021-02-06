import stripe
import json
import os
from lib.webexception import WebException
from http import HTTPStatus

# Stripe secret key
stripe.api_key = os.environ("STRIPE_SECRET_KEY")


def get_publishable_key(request, response):
    response.body = {
        "publishableKey": os.environ("STRIPE_PUBLISHABLE_KEY"),
        "basicPrice": os.environ("FREE_PRICE_ID"),
        "proPrice": os.environ("PRO_PRICE_ID"),
    }
    return response


def get_checkout_session(request, response):
    id = request.args.get("sessionId")
    response.body = stripe.checkout.Session.retrieve(id)
    return response


def create_checkout_session(request, response):
    data = request.data
    domain_url = os.environ("URL")

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [customer_email] - lets you prefill the email input in the form

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "/Success.html?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/Cancel.html",
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": data["priceId"], "quantity": 1}],
        )
        response.body = {"sessionId": checkout_session["id"]}
        return response
    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def customer_portal(request, response):
    data = request.data
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
    checkout_session_id = data["sessionId"]
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = os.environ("URL")

    session = stripe.billing_portal.Session.create(
        customer=checkout_session.customer, return_url=return_url
    )
    response.body = {"url": session.url}
    return response


def webhook_received(request, response):
    webhook_secret = os.environ("STRIPE_WEBHOOK_SECRET")
    request_data = request.data
    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret
            )
            data = event["data"]
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    data_object = data["object"]

    print("event " + event_type)

    if event_type == "checkout.session.completed":
        print("Payment succeeded!")

    return response

