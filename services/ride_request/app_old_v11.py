import json
import uuid
from datetime import datetime, timezone
import boto3

RIDE_REQUESTS_TABLE = "RideRequests"


class HttpResponse:
    def __init__(self, status_code, data=None, error_message=None):
        self.status_code = status_code
        self.data = data
        self.error_message = error_message
        self.is_success = status_code < 400

    def to_dict(self):
        return {
            "statusCode": self.status_code,
            "body": json.dumps(
                self.data if self.is_success else {"message": self.error_message}
            ),
            "headers": {"Content-Type": "application/json"},
        }


class SuccessResponse(HttpResponse):
    def __init__(self, data=None):
        super().__init__(status_code=200, data=data)


class CreatedResponse(HttpResponse):
    def __init__(self, data=None):
        super().__init__(status_code=201, data=data)


class BadRequestResponse(HttpResponse):
    def __init__(self, error_message):
        super().__init__(status_code=400, error_message=error_message)


class InternalServerErrorResponse(HttpResponse):
    def __init__(self, error_message):
        super().__init__(status_code=500, error_message=error_message)


class RequestValidator:
    def validate(self, body):
        required_fields = ["customerId", "pickupLocation", "destinationLocation"]
        missing_fields = [field for field in required_fields if field not in body]

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            return BadRequestResponse(f"Missing required fields: {missing_fields_str}")

        return SuccessResponse()


class RideRequestDynamoDBStorage:
    def __init__(self, dynamodb_client):
        self.dynamodb_client = dynamodb_client
        self.ride_id = str(uuid.uuid4())
        # Get current UTC timestamp with timezone
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def __build_item(self, body):
        try:
            item = {
                "rideId": {"S": self.ride_id},
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
                        "longitude": {
                            "N": str(body["destinationLocation"]["longitude"])
                        },
                    }
                },
                "status": {"S": "requested"},
                "timestamp": {"S": self.timestamp},
            }
            return SuccessResponse(item)
        except KeyError as e:
            return BadRequestResponse(f"Missing required field: {e}")

    def store(self, body):
        try:
            item = self.__build_item(body)

            if item.status_code != 200:
                return item

            self.dynamodb_client.put_item(TableName=RIDE_REQUESTS_TABLE, Item=item.data)
            return CreatedResponse()
        except Exception as e:
            return InternalServerErrorResponse(
                f"Failed to store ride request in DynamoDB: {e}"
            )


class RideRequestHandler:
    def __init__(
        self,
        request_validator: RequestValidator,
        ride_request_storage: RideRequestDynamoDBStorage,
    ):
        self.request_validator = request_validator
        self.ride_request_storage = ride_request_storage

    def handle(self, event, context):
        try:
            # Parse request body
            body = json.loads(event["body"])

            validation_result = self.request_validator.validate(body)

            if validation_result.status_code != 200:
                return validation_result

            # Store the ride request in DynamoDB
            ride_request_store_result = self.ride_request_storage.store()

            if ride_request_store_result.status_code != 201:
                return ride_request_store_result

            ride_id = ride_request_store_result.ride_id

            result = self.generate_success_response(ride_id)

            return result
        except json.JSONDecodeError:
            return BadRequestResponse("Invalid JSON in request body")
        except Exception:
            return InternalServerErrorResponse("Internal Server Error")

    def generate_success_response(self, ride_id):
        try:
            response_body = {
                "rideId": ride_id,
                "status": "requested",
                "estimatedArrivalTime": self.calculate_estimated_arrival_time(),
            }
            return SuccessResponse(response_body)
        except Exception as e:
            return InternalServerErrorResponse(
                f"Failed to generate success response: {e}"
            )

    def calculate_estimated_arrival_time(self):
        # Placeholder function for calculating estimated arrival time
        # You can replace this with actual logic
        return "2024-08-31T12:00:00Z"


def format_lambda_response(result):
    return {
        "statusCode": result.status_code,
        "body": json.dumps(
            result.data if result.data else {"message": result.error_message}
        ),
        "headers": {"Content-Type": "application/json"},
    }


def wrapped_lambda_handler(event, context):
    dynamodb_client = boto3.client("dynamodb")
    request_validator = RequestValidator()
    ride_request_storage = RideRequestDynamoDBStorage(dynamodb_client)
    lambda_handler = RideRequestHandler(request_validator, ride_request_storage)
    result = lambda_handler.handle(event, context)
    formatted_response = format_lambda_response(result)
    return formatted_response
