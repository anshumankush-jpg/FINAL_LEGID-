# Test all LEGID systems
$baseUrl = "http://localhost:8000"

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "TESTING ALL 4 LEGID SYSTEMS" -ForegroundColor Cyan
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: LEGID Master
Write-Host "TEST 1: LEGID Master Prompt" -ForegroundColor Yellow
Write-Host "Endpoint: /api/chat/legid" -ForegroundColor Gray
Write-Host ""

$body1 = @{
    message = "What are my Charter rights if I am arrested in Canada?"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/api/chat/legid" -Method Post -Body $body1 -ContentType "application/json" -ErrorAction Stop
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Response length: $($response1.answer.Length) characters" -ForegroundColor Green
    Write-Host "Confidence: $($response1.confidence)" -ForegroundColor Green
    Write-Host ""
    Write-Host "First 500 characters:" -ForegroundColor Gray
    Write-Host $response1.answer.Substring(0, [Math]::Min(500, $response1.answer.Length)) -ForegroundColor White
    Write-Host "..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 2: Ontario LTB Specialist
Write-Host "TEST 2: Ontario LTB Specialist" -ForegroundColor Yellow
Write-Host "Endpoint: /api/chat/legid/ontario-ltb" -ForegroundColor Gray
Write-Host ""

$body2 = @{
    message = "How does Form N4 work for non-payment of rent in Ontario?"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/api/chat/legid/ontario-ltb" -Method Post -Body $body2 -ContentType "application/json" -ErrorAction Stop
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Response length: $($response2.answer.Length) characters" -ForegroundColor Green
    Write-Host "Confidence: $($response2.confidence)" -ForegroundColor Green
    Write-Host ""
    Write-Host "First 500 characters:" -ForegroundColor Gray
    Write-Host $response2.answer.Substring(0, [Math]::Min(500, $response2.answer.Length)) -ForegroundColor White
    Write-Host "..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 3: Canada-USA Master
Write-Host "TEST 3: Canada-USA Master (4-Layer Reasoning)" -ForegroundColor Yellow
Write-Host "Endpoint: /api/chat/legid/canada-usa" -ForegroundColor Gray
Write-Host ""

$body3 = @{
    message = "Do I have to file taxes in Canada if I earn under dollar 20,000 per year?"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl/api/chat/legid/canada-usa" -Method Post -Body $body3 -ContentType "application/json" -ErrorAction Stop
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Response length: $($response3.answer.Length) characters" -ForegroundColor Green
    Write-Host "Confidence: $($response3.confidence)" -ForegroundColor Green
    Write-Host ""
    Write-Host "First 500 characters:" -ForegroundColor Gray
    Write-Host $response3.answer.Substring(0, [Math]::Min(500, $response3.answer.Length)) -ForegroundColor White
    Write-Host "..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 4: RAG-First Production (THE COMPLETE SYSTEM)
Write-Host "TEST 4: RAG-First Production (THE COMPLETE SYSTEM)" -ForegroundColor Yellow
Write-Host "Endpoint: /api/chat/legid/rag-production" -ForegroundColor Gray
Write-Host ""

$body4 = @{
    message = "Do I have to file taxes in Canada if I earn under dollar 20,000 per year?"
} | ConvertTo-Json

try {
    $response4 = Invoke-RestMethod -Uri "$baseUrl/api/chat/legid/rag-production" -Method Post -Body $body4 -ContentType "application/json" -ErrorAction Stop
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Response length: $($response4.answer.Length) characters" -ForegroundColor Green
    Write-Host "Confidence: $($response4.confidence)" -ForegroundColor Green
    Write-Host "Practice areas supported: $($response4.metadata.practice_areas_supported)" -ForegroundColor Green
    Write-Host ""
    Write-Host "First 500 characters:" -ForegroundColor Gray
    Write-Host $response4.answer.Substring(0, [Math]::Min(500, $response4.answer.Length)) -ForegroundColor White
    Write-Host "..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================================================" -ForegroundColor Cyan
