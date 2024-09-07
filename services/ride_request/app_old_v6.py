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
        result = build_ride_request_dynamodb_item(body, ride_id)

        if not result.is_success:
            return {
                "statusCode": result.status_code,
                "body": json.dumps({"message": result.error_message}),
                "headers": {"Content-Type": "application/json"},
            }

        # Store the ride request in DynamoDB
        result = store_ride_request_in_dynamodb(result.data)

        if not result.is_success:
            return {
                "statusCode": result.status_code,
                "body": json.dumps({"message": result.error_message}),
                "headers": {"Content-Type": "application/json"},
            }

        result = generate_success_response(ride_id)

        if not result.is_success:
            return {
                "statusCode": result.status_code,
                "body": json.dumps({"message": result.error_message}),
                "headers": {"Content-Type": "application/json"},
            }

        return {
            "statusCode": result.status_code,
            "body": json.dumps(result.data),
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error"}),
            "headers": {"Content-Type": "application/json"},
        }


def build_ride_request_dynamodb_item(body, ride_id):
    # Get current UTC timestamp with timezone
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
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
        return Result.success(item)
    except KeyError as e:
        return Result.failure(f"Missing required field: {e}", status_code=400)


def store_ride_request_in_dynamodb(item):
    try:
        dynamodb.put_item(TableName=RIDE_REQUESTS_TABLE, Item=item)
        return Result.success()
    except Exception as e:
        return Result.failure(
            f"Failed to store ride request in DynamoDB: {e}", status_code=500
        )


def generate_success_response(ride_id):
    try:
        response_body = {
            "rideId": ride_id,
            "status": "requested",
            "estimatedArrivalTime": calculate_estimated_arrival_time(),
        }
        return Result.success(response_body)
    except Exception as e:
        return Result.failure(
            f"Failed to generate success response: {e}", status_code=500
        )


def calculate_estimated_arrival_time():
    # Placeholder function for calculating estimated arrival time
    # You can replace this with actual logic
    return "2024-08-31T12:00:00Z"


class Result:
    def __init__(self, success, status_code, data=None, error_message=None):
        self.is_success = success
        self.status_code = status_code
        self.data = data
        self.error_message = error_message

    @staticmethod
    def success(data=None, status_code=200):
        return Result(True, status_code, data)

    @staticmethod
    def failure(error_message, status_code=500):
        return Result(False, status_code, error_message=error_message)
