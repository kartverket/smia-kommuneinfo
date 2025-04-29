#!/bin/bash

DEV_URL="https://kommuneinfo.atkv3-dev.kartverket-intern.cloud/kommuneinfo/v1"
TEST_URL="https://api.test.kartverket.no/kommuneinfo/v1/"
PROD_URL="https://api.kartverket.no/kommuneinfo/v1/"
# --- End Configuration ---

TEST_FILE="tests/integration/test_api.tavern.yaml"

if [ -z "$1" ]; then
  echo "Usage: $0 <environment>"
  echo "Available environments: dev, test, prod"
  exit 1
fi

ENVIRONMENT=$1
TARGET_URL=""

case $ENVIRONMENT in
  dev)
    TARGET_URL=$DEV_URL
    ;;
  test)
    TARGET_URL=$TEST_URL
    ;;
  prod)
    TARGET_URL=$PROD_URL
    ;;
  *)
    echo "Error: Invalid environment '$ENVIRONMENT'."
    echo "Available environments: dev, test, prod"
    exit 1
    ;;
esac

if [[ "$TARGET_URL" == "<REPLACE_WITH_"* ]]; then
  echo "Error: Placeholder URL found for environment '$ENVIRONMENT'."
  echo "Please edit '$0' and replace the placeholder URL before running."
  exit 1
fi

echo "Running tests against environment: $ENVIRONMENT"
echo "Target URL: $TARGET_URL"
echo "Test file: $TEST_FILE"
echo "---"

export TAVERN_TEST_URL=$TARGET_URL
tavern-ci "$TEST_FILE"

EXIT_CODE=$?

echo "---"
echo "Tavern tests finished with exit code: $EXIT_CODE"

# Exit with the same code as tavern-ci
exit $EXIT_CODE 