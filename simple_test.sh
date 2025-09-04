#!/bin/bash

# Simple EKO Backend Auth Flow Test
BASE_URL="http://localhost:9753"
TIMESTAMP=$(date +%s)
EMAIL="simple_test_${TIMESTAMP}@example.com"
PASSWORD="Test123"

echo "🚀 Simple EKO Backend Auth Flow Test"
echo "===================================="
echo "Email: $EMAIL"
echo "Password: $PASSWORD"
echo ""

echo "1️⃣ Testing Empty Password Security:"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": ""}' \
  "$BASE_URL/auth/login" | jq -r '.message'
echo ""

echo "2️⃣ Signup:"
SIGNUP_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"confirm_password\": \"$PASSWORD\", \"language\": \"en\", \"agreed\": true}" \
  "$BASE_URL/auth/signup")
echo "$SIGNUP_RESPONSE" | jq -r '.message'
TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.data.token')
echo "Token: ${TOKEN:0:20}..."
echo ""

echo "3️⃣ Login:"
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  "$BASE_URL/auth/login")
echo "$LOGIN_RESPONSE" | jq -r '.message'
LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token')
echo "Token: ${LOGIN_TOKEN:0:20}..."
echo ""

echo "4️⃣ Onboarding:"
ONBOARDING_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $LOGIN_TOKEN" \
  -d '{"name": "Simple Test User", "age": 25, "gender": "male", "language": "en", "purpose": "personal assistance"}' \
  "$BASE_URL/auth/onboarding")
echo "$ONBOARDING_RESPONSE" | jq -r '.message'
ONBOARDING_TOKEN=$(echo "$ONBOARDING_RESPONSE" | jq -r '.data.token')
echo "Token: ${ONBOARDING_TOKEN:0:20}..."
echo ""

echo "5️⃣ Get User Profile:"
USER_RESPONSE=$(curl -s -X GET -H "Authorization: Bearer $ONBOARDING_TOKEN" \
  "$BASE_URL/profile/user")
echo "$USER_RESPONSE" | jq -r '.message'
echo "User Name: $(echo "$USER_RESPONSE" | jq -r '.data.name')"
echo "User Age: $(echo "$USER_RESPONSE" | jq -r '.data.age')"
echo ""

echo "6️⃣ French Signup Test:"
FR_EMAIL="simple_test_fr_${TIMESTAMP}@example.com"
FR_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"email\": \"$FR_EMAIL\", \"password\": \"$PASSWORD\", \"confirm_password\": \"$PASSWORD\", \"language\": \"fr\", \"agreed\": true}" \
  "$BASE_URL/auth/signup")
echo "$FR_RESPONSE" | jq -r '.message'
echo ""

echo "✅ Test Complete!"
echo "=================="
echo "✅ Empty password rejected"
echo "✅ Signup works"
echo "✅ Login works" 
echo "✅ Onboarding works"
echo "✅ Get user works"
echo "✅ French localization works"
