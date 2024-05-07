import azure.functions as func
import json
import os
import logging
from .rocketscraper import getData, getFilteredRankData

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse the API key from the route parameter
        api_key = req.route_params.get('api_key')

        # Load the allowed users data
        allowed_users_path = os.path.join(os.path.dirname(__file__), '..', 'allowed_users.json')
        with open(allowed_users_path, 'r') as file:
            allowed_users = json.load(file)

        # Check if the API key is in the allowed users list
        user = next((user for user in allowed_users if user['userkey'] == api_key), None)
        if not user:
            return func.HttpResponse("Unauthorized", status_code=401)

        # Use the details from the allowed users to fetch data
        full_data = await getData(user['username'], user['platform'])

        if full_data is None or 'data' not in full_data or 'segments' not in full_data['data']:
            logging.error(f"Data fetched is not as expected: {full_data}")
            return func.HttpResponse("Error fetching data or 'segments' key not found", status_code=500)

        # Parse query parameters for hidden playlists and options
        hiddenPlaylists = []
        hiddenOptions = []
        for key, value in req.params.items():
            if value.lower() == 'false':
                hiddenPlaylists.append(key)
            if key == 'div' and value.lower() == 'false':
                hiddenOptions.append(key)

        # Filter rank data
        data = full_data['data']  # Access the 'data' key
        rank_data = getFilteredRankData(data, hiddenPlaylists, hiddenOptions)

        # Return the filtered rank data as plain text
        return func.HttpResponse(rank_data, mimetype="text/plain")

    except Exception as e:
        # Log the exception
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)