import json
import uuid
from datetime import datetime, timezone
import boto3

dynamodb = boto3.client("dynamodb")

RIDE_REQUESTS_TABLE = "RideRequests"


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        ride_id = str(uuid.uuid4())

        # Build the ride request item for DynamoDB
        ride_request_dynamodb_item = build_ride_request_dynamodb_item(body, ride_id)

        # Store the ride request in DynamoDB
        store_ride_request_in_dynamodb(ride_request_dynamodb_item)

        return generate_success_response(ride_id)

    except Exception as e:
        print(e)
        return generate_error_response()


def build_ride_request_dynamodb_item(body, ride_id):
    # Get current UTC timestamp with timezone
    timestamp = datetime.now(timezone.utc).isoformat()

    item = {
        "rideId": {"S": ride_id},
        "customerId": {"S": body["customerId"]},
        "pickupLocation": {
            "M": {
                "latitude": {"N": str(body["pickupLocation"]["latitude"])},
                "longitude": {"N": str(body["pickupLocation"]["longitude"])},
            }
        },
        "destinationLocation": {
            "M": {
                "latitude": {"N": str(body["destinationLocation"]["latitude"])},
                "longitude": {"N": str(body["destinationLocation"]["longitude"])},
            }
        },
        "status": {"S": "requested"},
        "timestamp": {"S": timestamp},
    }
    return item


def store_ride_request_in_dynamodb(item):
    dynamodb.put_item(TableName=RIDE_REQUESTS_TABLE, Item=item)


def generate_success_response(ride_id):
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "rideId": ride_id,
                "status": "requested",
                "estimatedArrivalTime": calculate_estimated_arrival_time(),
            }
        ),
        "headers": {"Content-Type": "application/json"},
    }


def generate_error_response():
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Internal Server Error"}),
        "headers": {"Content-Type": "application/json"},
    }


def calculate_estimated_arrival_time():
    # Placeholder function for calculating estimated arrival time
    # You can replace this with actual logic
    return "2024-08-31T12:00:00Z"
