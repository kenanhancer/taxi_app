import os

import boto3
import pytest
import requests

from services.tests.integration.stack_name_not_set_error import StackNameNotSetError
from services.tests.integration.stack_not_found_error import StackNotFoundError

# Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to tes


class TestApiGateway:

    @pytest.fixture()
    def api_gateway_url(self):
        """Get the API Gateway URL from Cloudformation Stack outputs"""
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise StackNameNotSetError()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise StackNotFoundError(
                f"Cannot find stack {stack_name} \n"
                f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [
            output for output in stack_outputs if output["OutputKey"] == "HelloWorldApi"
        ]

        if not api_outputs:
            raise KeyError(f"HelloWorldAPI not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"]  # Extract url from stack outputs

    def test_api_gateway(self, api_gateway_url):
        """Call the API Gateway endpoint and check the response"""
        response = requests.get(api_gateway_url)

        assert response.status_code == 200
        assert response.json() == {"message": "hello world"}
