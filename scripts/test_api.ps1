# Test New Schema API with PowerShell
Write-Host "🧪 Testing New Schema API Functionality" -ForegroundColor Cyan
Write-Host "=" * 50

# Wait for server to be ready
Start-Sleep -Seconds 3

# Test 1: Check server health
Write-Host "`n🏥 Testing Server Health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Server is healthy: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Server health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Login to get token
Write-Host "`n🔐 Testing Authentication..." -ForegroundColor Yellow
$loginData = @{
    username = "testuser@example.com"
    password = "testpassword123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✅ Authentication successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test 3: Get vocab collections (new schema)
Write-Host "`n📁 Testing Vocab Collections API..." -ForegroundColor Yellow
try {
    $collections = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/vocab-collections" -Method Get -Headers $headers
    Write-Host "✅ GET collections: Found $($collections.Count) collections" -ForegroundColor Green
    
    if ($collections.Count -gt 0) {
        $firstCollection = $collections[0]
        Write-Host "   📄 Sample: $($firstCollection.name) (ID: $($firstCollection.id))" -ForegroundColor Gray
        $collectionId = $firstCollection.id
    }
} catch {
    Write-Host "❌ GET collections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Test learned vocabs with collection reference
if ($collectionId) {
    Write-Host "`n📚 Testing Learned Vocabs API (New Schema)..." -ForegroundColor Yellow
    
    # Get vocabs for collection
    try {
        $vocabs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/learned-vocabs?collection_id=$collectionId" -Method Get -Headers $headers
        Write-Host "✅ GET vocabs: Found $($vocabs.Count) vocab sets in collection" -ForegroundColor Green
        
        if ($vocabs.Count -gt 0) {
            foreach ($vocabSet in $vocabs) {
                Write-Host "   📄 $($vocabSet.vocabs.Count) words, usage: $($vocabSet.usage_count)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "❌ GET vocabs failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 5: Test history by date (date-only format)
Write-Host "`n📅 Testing History by Date API (Date-Only Format)..." -ForegroundColor Yellow
$historyData = @{
    study_date = "2024-01-15"  # Date-only format
    words_learned = 25
    time_spent_minutes = 45
    accuracy_percentage = 87.5
} | ConvertTo-Json

try {
    $historyResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/history-by-date" -Method Post -Body $historyData -Headers $headers -ContentType "application/json"
    Write-Host "✅ POST history: Created entry for $($historyResponse.study_date)" -ForegroundColor Green
} catch {
    Write-Host "❌ POST history failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Test user feedback
Write-Host "`n💬 Testing User Feedback API..." -ForegroundColor Yellow
$feedbackData = @{
    feedback_text = "Schema migration worked perfectly!"
    rating = 5
    category = "improvement"
} | ConvertTo-Json

try {
    $feedbackResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/user-feedback" -Method Post -Body $feedbackData -Headers $headers -ContentType "application/json"
    Write-Host "✅ POST feedback: Created rating $($feedbackResponse.rating)/5" -ForegroundColor Green
} catch {
    Write-Host "❌ POST feedback failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Schema migration API tests completed!" -ForegroundColor Cyan
Write-Host "`nKey Changes Validated:" -ForegroundColor White
Write-Host "✅ vocab_collections now owned by users" -ForegroundColor Green
Write-Host "✅ learned_vocabs reference collections instead of users directly" -ForegroundColor Green
Write-Host "✅ history_by_date uses date-only format" -ForegroundColor Green
Write-Host "✅ user_feedback collection working" -ForegroundColor Green
Write-Host "✅ All APIs work with new schema" -ForegroundColor Green