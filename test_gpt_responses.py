import os
import openai
from AirbnbReply import generate_response

# Set OpenAI API Key
with open("openai_key.txt", "r") as f:
    openai.api_key = f.read().strip()

# Read Airbnb info
with open("airbnb_info.txt", "r") as f:
    airbnb_info = f.read().strip()

# Test messages that should have sufficient info
sufficient_messages = [
    "What's the parking situation?",
    "Do you have AC in the unit?",
    "How does the shower work?",
    "Is there cable TV?",
]

# Test messages that should have insufficient info
insufficient_messages = [
    "What restaurants do you recommend nearby?",  # No info about nearby restaurants
    "Is there a gym in the building?",  # No info about building amenities
    "What floor is the apartment on?",  # No floor info provided
    "How far is it from Pike Place Market?",  # No specific location info
]

# Test messages that don't need a response
no_response_messages = [
    "Thanks for the information! Looking forward to my stay.",
    "Got it, thanks!",
    "Perfect, that's exactly what I needed to know.",
    "Thank you for confirming. Have a great day!",
    "Thanks for the quick response about the parking.",
]

print("\nTesting messages that should have sufficient info:")
print("=" * 50)
for msg in sufficient_messages:
    print(f"\nTesting message: {msg}")
    response = generate_response(msg, airbnb_info)
    print(f"Response:\n{response}\n")
    print("-" * 30)

print("\nTesting messages that should have insufficient info:")
print("=" * 50)
for msg in insufficient_messages:
    print(f"\nTesting message: {msg}")
    response = generate_response(msg, airbnb_info)
    print(f"Response:\n{response}\n")
    print("-" * 30)

print("\nTesting messages that don't need a response:")
print("=" * 50)
for msg in no_response_messages:
    print(f"\nTesting message: {msg}")
    response = generate_response(msg, airbnb_info)
    print(f"Response:\n{response}\n")
    print("-" * 30)
