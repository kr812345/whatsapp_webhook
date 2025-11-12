# WhatAPI (whapi.py) — README

## Overview
WhatAPI is a small FastAPI application that provides simple HTTP endpoints to send WhatsApp messages (text and image) and to broadcast messages to multiple recipients. The service acts as a thin wrapper around an external WhatsApp API (configured via environment variables) and exposes three primary endpoints for use by other services or tools.

## Features
- Send a single text message to a phone number.
- Send a single image (with optional caption) to a phone number.
- Broadcast a text or image message to multiple phone numbers.
- Uses Pydantic models for request validation.
- Environment-driven configuration for API token and base URL.

## Requirements
- Python 3.8+
- Packages:
    - fastapi
    - uvicorn
    - python-dotenv
    - pydantic
    - requests

## Environment Variables
The application reads configuration from environment variables (via python-dotenv):
- WHAPI_TOKEN — Bearer token used to authorize requests to the external WhatsApp API.
- WHAPI_BASEURL — Base URL of the external WhatsApp API (e.g., `https://api.example.com`).

Make sure a `.env` file (or environment) provides these values before starting the app.

## Installation
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
     pip install fastapi uvicorn python-dotenv pydantic requests

4. Create a `.env` file with:
     WHAPI_TOKEN=your_api_token
     WHAPI_BASEURL=https://your-whapi-base-url

## Running
Start the app with:
uvicorn whapi:app --host 0.0.0.0 --port 8000

Alternatively, run the module directly:
python whapi.py

## API Endpoints

1. GET /
- Description: Health/welcome endpoint to verify the app is running.
- Response: Simple string message indicating the service is running.

2. POST /send/text
- Description: Send a single text message to a phone number.
- Request JSON body (validated with Pydantic):
    {
        "phone_number": "<recipient_phone_number>",
        "message": "<text_message>"
    }
- Success Response: JSON object containing status and the upstream API response in the `data` field.
- Error Handling: Returns 400 on exceptions.

3. POST /send/image
- Description: Send an image (remote URL) to a phone number, with an optional caption.
- Request JSON body:
    {
        "phone_number": "<recipient_phone_number>",
        "image_url": "<url_to_image>",
        "caption": "<optional_caption>"
    }
- Success Response: JSON with status and upstream API response.
- Error Handling: Returns 400 on exceptions.

4. POST /broadcast
- Description: Broadcast a message to multiple phone numbers. Supports `text` and `image` message types.
- Request JSON body:
    {
        "numbers": ["+1234567890", "+1987654321"],
        "message": "Hello recipients",
        "message_type": "text",         // optional, defaults to "text"
        "image_url": "https://..."      // optional, required if message_type is "image"
    }
- Behavior: Iterates through the provided numbers and calls the appropriate send function for each recipient. Returns an array of upstream API responses.
- Error Handling: Returns 400 on exceptions.

## Request Authorization & External Calls
- Outbound requests to the external WhatsApp API include an `Authorization: Bearer <WHAPI_TOKEN>` header.
- Paths used to call the external API are constructed from `WHAPI_BASEURL` appended with `/messages/text` or `/messages/image`.
- The app relies on the external service to perform actual message delivery; responses from that service are relayed back to the caller verbatim in the `data` field.

## Response Format
On success, endpoints return:
{
    "status": "success",
    "data": <response_from_upstream_api_or_array_of_responses>
}

On error, the API raises an HTTPException (commonly with status code 400), and returns details of the exception.

## Notes & Considerations
- Input validation is performed via Pydantic models. Ensure request payloads conform to the expected shapes.
- The application performs synchronous HTTP requests (requests library) to the external API. For high throughput or production usage, consider:
    - Switching to asynchronous HTTP client (e.g., httpx) and making the FastAPI handlers async.
    - Adding retry/backoff logic for transient network errors.
    - Implementing rate limiting and batching for broadcasts to avoid throttling by the upstream API.
- Error handling is basic; you may want to add structured logging and more granular HTTP status codes.
- Ensure secure storage of the WHAPI_TOKEN; do not commit `.env` files containing secrets.

## Example curl usage
- Send text:
    curl -X POST http://localhost:8000/send/text -H "Content-Type: application/json" -d '{"phone_number":"+1234567890","message":"Hello"}'

- Send image:
    curl -X POST http://localhost:8000/send/image -H "Content-Type: application/json" -d '{"phone_number":"+1234567890","image_url":"https://example.com/img.jpg","caption":"Nice pic"}'

- Broadcast:
    curl -X POST http://localhost:8000/broadcast -H "Content-Type: application/json" -d '{"numbers":["+123","+456"],"message":"Hello everyone","message_type":"text"}'

## License
Include your project's license here (e.g., MIT) as appropriate.
