#!/bin/bash

echo "🔍 Verification Test: Custom Day Function Consistency"
echo "======================================================"
echo ""

echo "Test 1: Query with start time at midnight"
echo "-------------------------------------------"
result1=$(docker-compose exec -T db psql -U postgres -d fxohlc -t -c "SELECT bucket FROM get_custom_day_ohlc('2025-12-03 00:00:00+00', '2025-12-05 00:00:00+00', 22) LIMIT 1;")
echo "Bucket: $result1"
echo ""

echo "Test 2: Query with start time at 10 AM (different!)"
echo "-----------------------------------------------------"
result2=$(docker-compose exec -T db psql -U postgres -d fxohlc -t -c "SELECT bucket FROM get_custom_day_ohlc('2025-12-04 10:00:00+00', '2025-12-05 00:00:00+00', 22) LIMIT 1;")
echo "Bucket: $result2"
echo ""

echo "Test 3: Query with start time at 5 PM (even more different!)"
echo "-------------------------------------------------------------"
result3=$(docker-compose exec -T db psql -U postgres -d fxohlc -t -c "SELECT bucket FROM get_custom_day_ohlc('2025-12-04 17:00:00+00', '2025-12-05 00:00:00+00', 22) LIMIT 1;")
echo "Bucket: $result3"
echo ""

echo "✅ Verification Result:"
echo "======================"
if [ "$result1" = "$result2" ] && [ "$result2" = "$result3" ]; then
    echo "✅ SUCCESS! All queries return the same bucket."
    echo "✅ Custom day function is working correctly!"
    echo ""
    echo "Bucket alignment: $result1"
    exit 0
else
    echo "❌ FAILURE! Buckets are inconsistent:"
    echo "   Query 1: $result1"
    echo "   Query 2: $result2"
    echo "   Query 3: $result3"
    exit 1
fi
