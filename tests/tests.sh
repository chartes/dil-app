#!/bin/bash

# Run the following commands to test :
# ./linter.sh
# pytest --tb=short -v --cov
# coverage-badge -o coverage.svg
#

BASE_DIR=".."
RCFILE=".pylintrc"
THRESHOLD=8.5
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="pylint_$DATE.log"

echo "Running pytest + coverage... ($DATE)" | tee -a $LOG_FILE 2>&1
pytest --tb=short -v --cov | tee -a $LOG_FILE 2>&1
echo "Running code Python quality tests... ($DATE)" | tee -a $LOG_FILE 2>&1
pylint $BASE_DIR/*.py --fail-under=$THRESHOLD | tee -a $LOG_FILE 2>&1
pylint $BASE_DIR/api/*.py --fail-under=$THRESHOLD | tee -a $LOG_FILE 2>&1
pylint $BASE_DIR/api/admin/*.py --fail-under=$THRESHOLD | tee -a $LOG_FILE 2>&1
echo "Done. See $LOG_FILE for details."
echo "Generating coverage badge..."
coverage-badge -o coverage.svg

