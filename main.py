# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.

import os
import stripe

from flask import Flask, redirect

app = Flask(__name__)

stripe.api_key = "sk_test_51M2wQrLHmOtV3dJutcUD4mPjLuQet2lumJbs990sqDOC3x2s8B7pXgkbI9hxAXG9hLseW5RKWwzq7PimDVttBPvg00bWaSic9s"


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "T-shirt",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:4242/success",
        cancel_url="http://localhost:4242/cancel",
    )

    return redirect(session.url, code=303)


if __name__ == "__main__":
    app.run(port=4242)
