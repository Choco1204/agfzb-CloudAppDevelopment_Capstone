import requests
import json
import logging

# import related models here


# Create a `get_request` to make HTTP GET requests
# Configure logger
logger = logging.getLogger(__name__)

# Define backend URL (update with your actual URL)
BACKEND_URL = "http://localhost:3000"
SENTIMENT_ANALYZER_URL = "http://localhost:5001"


def get_request(endpoint, **kwargs):
    """
    Make a GET request to the specified endpoint with URL parameters
    Args:
        endpoint (str): API endpoint path (e.g., 'reviews')
        **kwargs: Arbitrary keyword arguments for URL parameters
    Returns:
        dict: JSON response if successful, None otherwise
    """
    try:
        # Construct full URL
        url = f"{BACKEND_URL.rstrip('/')}/{endpoint.lstrip('/')}"

        # Log the request
        logger.info(f"Making GET request to: {url}")
        logger.debug(f"Parameters: {kwargs}")

        # Make the request with proper timeout and params handling
        response = requests.get(url, params=kwargs, timeout=10)  # 10-second timeout

        # Raise exception for 4xx/5xx status codes
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return None
    except ValueError as e:  # JSON decode error
        logger.error(f"Failed to decode JSON response: {str(e)}")
        return None


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(endpoint, json_payload, **kwargs):
    """
    Make a HTTP POST request
    Args:
        endpoint (str): API endpoint path
        json_payload (dict): JSON data to send in request body
        **kwargs: Additional URL parameters
    Returns:
        dict: JSON response if successful, None otherwise
    """
    try:
        url = f"{SENTIMENT_ANALYZER_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.info(f"Making POST request to: {url}")

        response = requests.post(url, json=json_payload, params=kwargs, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"POST request failed: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Failed to decode JSON response: {str(e)}")
        return None


def post_review(data_dict):
    """
    Submit a dealership review to the backend service
    Args:
        data_dict (dict): Review data containing:
            - id (required)
            - dealership
            - name
            - purchase
            - review
            - purchase_date (optional)
            - car_model (optional)
    Returns:
        dict: Created review data or error message
    """
    try:
        endpoint = "/insert_review"
        url = f"{BACKEND_URL.rstrip('/')}/{endpoint.lstrip('/')}"

        logger.info(f"Submitting review to: {url}")
        logger.debug(f"Review data: {data_dict}")

        response = requests.post(url, json=data_dict, timeout=10)  # 10-second timeout
        response.raise_for_status()

        logger.info("Review submitted successfully")
        return response.json()

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error submitting review: {e.response.text}")
        return {"error": f"Validation error: {e.response.json().get('message', '')}"}
    except requests.exceptions.ConnectionError:
        logger.error("Connection failed - is backend service running?")
        return {"error": "Backend service unavailable"}
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return {"error": "Request timeout"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": "Failed to submit review"}


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    """
    Analyze review text using sentiment analysis microservice
    Args:
        text (str): Review text to analyze
    Returns:
        dict: Sentiment analysis results or error message
    """
    if not text:
        return {"error": "No text provided for analysis"}

    try:
        return post_request("analyze", json_payload={"text": text})
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return {"error": "Sentiment analysis service unavailable"}
