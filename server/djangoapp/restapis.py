import requests
import json
import logging

# import related models here


# Create a `get_request` to make HTTP GET requests
# Configure logger
logger = logging.getLogger(__name__)

# Define backend URL (update with your actual URL)
BACKEND_URL = "https://devyann12-3030.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai"


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
