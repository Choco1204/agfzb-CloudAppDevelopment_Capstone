from flask import Flask, jsonify, request
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
import os

app = Flask(__name__)

# IBM NLU Credentials (For production, use environment variables)
NLU_URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/33184a89-3005-438f-80b2-ddcc80e62740"
NLU_APIKEY = "Tcq7ZK70YSSHNbl0XZ77ep7P5X0m1ZaVnmkeWEz0dANT"

# Initialize NLU client
authenticator = IAMAuthenticator(NLU_APIKEY)
nlu = NaturalLanguageUnderstandingV1(version="2022-04-07", authenticator=authenticator)
nlu.set_service_url(NLU_URL)


@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    try:
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        response = nlu.analyze(
            text=text, features=Features(sentiment=SentimentOptions())
        ).get_result()

        return jsonify(
            {
                "sentiment": response["sentiment"]["document"]["label"],
                "score": response["sentiment"]["document"]["score"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
