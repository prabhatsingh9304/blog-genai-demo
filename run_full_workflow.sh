#!/bin/bash
set -e

# Change to the script's directory to ensure paths work correctly
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo "Running from directory: $(pwd)"

# Load environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  # Safely load .env file, ignoring errors
  set +e
  export $(grep -v '^#' .env | xargs -r 2>/dev/null)
  set -e
  echo "Environment variables loaded."
else
  echo "No .env file found. Looking for API keys in environment..."
fi

# Clean API keys (remove carriage returns, newlines, whitespace)
if [ -n "$OPENAI_API_KEY" ]; then
  OPENAI_API_KEY=$(echo "$OPENAI_API_KEY" | tr -d '\r\n ')
  export OPENAI_API_KEY
  echo "Cleaned OPENAI_API_KEY"
fi

if [ -n "$OPENROUTER_API_KEY" ]; then
  OPENROUTER_API_KEY=$(echo "$OPENROUTER_API_KEY" | tr -d '\r\n ')
  export OPENROUTER_API_KEY
  echo "Cleaned OPENROUTER_API_KEY"
fi

# Colors for better output
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}  TESTING COMPLETE BLOG GENERATION WORKFLOW   ${NC}"
echo -e "${BLUE}===============================================${NC}"

# Create test output directory
TEST_DIR="blog/workflow_test"
mkdir -p $TEST_DIR

# Check if directory was created successfully
if [ ! -d "$TEST_DIR" ]; then
  echo -e "${RED}Error: Could not create output directory $TEST_DIR${NC}"
  exit 1
fi

# Step 1: Check for API keys
echo -e "\n${YELLOW}Step 1: Checking environment...${NC}"
if [ -z "$OPENAI_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ]; then
  echo -e "${RED}Error: No API keys found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY.${NC}"
  echo "For testing purposes, you can set a temporary key:"
  echo "export OPENAI_API_KEY=your-key-here"
  exit 1
else
  echo -e "${GREEN}API key found. Continuing...${NC}"
fi

# Detect Python command (python or python3)
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "Using python3 command"
    else
        echo -e "${RED}Error: Neither python nor python3 command found. Please install Python.${NC}"
        exit 1
    fi
fi

# Step 2: Test trending topics with local analysis
echo -e "\n${YELLOW}Step 2: Testing local trend analysis...${NC}"
echo -e "Listing trending keywords using local content analyzer..."
$PYTHON_CMD example.py --list-keywords --local-trends

# Step 3: Test blog generation with local trends
echo -e "\n${YELLOW}Step 3: Generating a blog post with local trend analysis...${NC}"
TOPIC="write a blog on persnal loan"
echo -e "Topic: ${GREEN}$TOPIC${NC}"
echo -e "Using model: ${GREEN}gpt-3.5-turbo${NC} (faster for testing)"
echo -e "Starting generation (this may take a minute)..."

# Run the blog generation with all components working together
$PYTHON_CMD example.py --topic "$TOPIC" \
                --model "gpt-3.5-turbo" \
                --local-trends \
                --output-dir "$TEST_DIR" \
                --temperature 0.7

# Step 4: List the generated blogs
echo -e "\n${YELLOW}Step 4: Verifying blog was created...${NC}"
$PYTHON_CMD example.py --list-blogs --output-dir "$TEST_DIR"

# Get the most recent blog file
BLOG_FILE=$(ls -t $TEST_DIR/*.md | head -1)

if [ -f "$BLOG_FILE" ]; then
  echo -e "\n${GREEN}SUCCESS! Full workflow test completed.${NC}"
  echo -e "Blog file created: ${GREEN}$BLOG_FILE${NC}"
  echo -e "\nPreview of generated blog:\n${BLUE}"
  head -n 10 "$BLOG_FILE"
  echo -e "${NC}..."
else
  echo -e "\n${RED}ERROR: Blog file was not created.${NC}"
  exit 1
fi

echo -e "\n${BLUE}===============================================${NC}"
echo -e "${GREEN}  ALL COMPONENTS WORKING CORRECTLY TOGETHER   ${NC}"
echo -e "${BLUE}===============================================${NC}" 