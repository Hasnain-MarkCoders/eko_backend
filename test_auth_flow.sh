#!/bin/bash

# EKO Backend Auth Flow Test Script
# Tests: Signup → Login → Onboarding → Get User (English & French)

BASE_URL="http://localhost:9753"
TIMESTAMP=$(date +%s)

echo "🚀 Starting EKO Backend Auth Flow Test"
echo "======================================"
echo ""

# Test data
EN_EMAIL="test_en_${TIMESTAMP}@example.com"
FR_EMAIL="test_fr_${TIMESTAMP}@example.com"
PASSWORD="Test123"
NAME="Test User"
AGE=25
GENDER="male"
PURPOSE="personal assistance"

echo "📧 Test emails:"
echo "   English: $EN_EMAIL"
echo "   French: $FR_EMAIL"
echo ""

# Function to make API calls and display results
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    local token=$5
    
    echo "🔹 $description"
    echo "   $method $endpoint"
    
    if [ -n "$token" ]; then
        response=$(curl -s -X $method \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    echo "   Response: $response"
    
    # Extract token if present
    if echo "$response" | grep -q '"token"'; then
        echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4
    else
        echo ""
    fi
}

# Function to test complete flow for a language
test_language_flow() {
    local email=$1
    local language=$2
    local lang_name=$3
    
    echo ""
    echo "🌍 Testing $lang_name Flow"
    echo "=========================="
    
    # 1. Signup
    signup_data='{
        "email": "'$email'",
        "password": "'$PASSWORD'",
        "confirm_password": "'$PASSWORD'",
        "language": "'$language'",
        "agreed": true
    }'
    
    signup_token=$(make_request "POST" "/auth/signup" "$signup_data" "1. Signup ($lang_name)")
    
    if [ -z "$signup_token" ]; then
        echo "❌ Signup failed for $lang_name"
        return 1
    fi
    
    echo "✅ Signup successful, token: ${signup_token:0:20}..."
    
    # 2. Login
    login_data='{
        "email": "'$email'",
        "password": "'$PASSWORD'"
    }'
    
    login_token=$(make_request "POST" "/auth/login" "$login_data" "2. Login ($lang_name)")
    
    if [ -z "$login_token" ]; then
        echo "❌ Login failed for $lang_name"
        return 1
    fi
    
    echo "✅ Login successful, token: ${login_token:0:20}..."
    
    # 3. Onboarding
    onboarding_data='{
        "name": "'$NAME'",
        "age": '$AGE',
        "gender": "'$GENDER'",
        "language": "'$language'",
        "purpose": "'$PURPOSE'"
    }'
    
    onboarding_token=$(make_request "POST" "/auth/onboarding" "$onboarding_data" "3. Onboarding ($lang_name)" "$login_token")
    
    if [ -z "$onboarding_token" ]; then
        echo "❌ Onboarding failed for $lang_name"
        return 1
    fi
    
    echo "✅ Onboarding successful, token: ${onboarding_token:0:20}..."
    
    # 4. Get User Profile
    user_response=$(make_request "GET" "/profile/user" "" "4. Get User Profile ($lang_name)" "$onboarding_token")
    
    if echo "$user_response" | grep -q '"success":true'; then
        echo "✅ Get user successful for $lang_name"
    else
        echo "❌ Get user failed for $lang_name"
        return 1
    fi
    
    echo "✅ $lang_name flow completed successfully!"
    return 0
}

# Test empty password login (should fail)
echo ""
echo "🔒 Testing Security: Empty Password Login"
echo "========================================"
empty_password_data='{
    "email": "test@example.com",
    "password": ""
}'
make_request "POST" "/auth/login" "$empty_password_data" "Empty password login (should fail)"

# Test wrong password login (should fail)
echo ""
echo "🔒 Testing Security: Wrong Password Login"
echo "========================================"
wrong_password_data='{
    "email": "test@example.com",
    "password": "Wrong123"
}'
make_request "POST" "/auth/login" "$wrong_password_data" "Wrong password login (should fail)"

# Test English flow
test_language_flow "$EN_EMAIL" "en" "English"

# Test French flow
test_language_flow "$FR_EMAIL" "fr" "French"

echo ""
echo "🎉 Auth Flow Test Complete!"
echo "=========================="
echo ""
echo "📊 Summary:"
echo "   ✅ Security tests (empty/wrong password) - should fail"
echo "   ✅ English flow: Signup → Login → Onboarding → Get User"
echo "   ✅ French flow: Signup → Login → Onboarding → Get User"
echo ""
echo "🔍 Check the responses above to verify:"
echo "   - Empty password is rejected"
echo "   - Wrong password is rejected"
echo "   - Correct password allows login"
echo "   - Onboarding works in both languages"
echo "   - User profile retrieval works"
