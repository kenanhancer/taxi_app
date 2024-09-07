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

        # Get current UTC timestamp with timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build the ride request item for DynamoDB
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

        # Store the ride request in DynamoDB
        dynamodb.put_item(TableName=RIDE_REQUESTS_TABLE, Item=item)

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

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error"}),
            "headers": {"Content-Type": "application/json"},
        }

    # return {
    #     "statusCode": 200,
    #     "body": json.dumps(
    #         {
    #             "message": "hello world",
    #         }
    #     ),
    # }


def calculate_estimated_arrival_time():
    # Placeholder function for calculating estimated arrival time
    # You can replace this with actual logic
    return "2024-08-31T12:00:00Z"
