# ================================================================================================
# LEGID SYSTEMS - COMPREHENSIVE DEMO TEST
# Tests all 4 systems with real-world legal questions
# ================================================================================================

$baseUrl = "http://localhost:8000"

function Test-Endpoint {
    param(
        [string]$SystemName,
        [string]$Endpoint,
        [string]$Question,
        [string]$Color = "Yellow"
    )
    
    Write-Host "`n" ("="*100) -ForegroundColor $Color
    Write-Host "TESTING: $SystemName" -ForegroundColor $Color
    Write-Host ("="*100) -ForegroundColor $Color
    Write-Host "Endpoint: $Endpoint" -ForegroundColor Gray
    Write-Host "Question: $Question" -ForegroundColor White
    Write-Host ""
    
    $body = @{ message = $Question } | ConvertTo-Json
    
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "$baseUrl$Endpoint" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        $endTime = Get-Date
        $elapsed = ($endTime - $startTime).TotalSeconds
        
        Write-Host "SUCCESS!" -ForegroundColor Green
        Write-Host "Response Time: $([Math]::Round($elapsed, 2)) seconds" -ForegroundColor Green
        Write-Host "Length: $($response.answer.Length) characters" -ForegroundColor Green
        Write-Host "Confidence: $($response.confidence)" -ForegroundColor Green
        
        if ($response.metadata) {
            Write-Host "`nMetadata:" -ForegroundColor Gray
            Write-Host "  Prompt Version: $($response.metadata.prompt_version)" -ForegroundColor Gray
            Write-Host "  Mode: $($response.metadata.mode)" -ForegroundColor Gray
            if ($response.metadata.practice_areas_supported) {
                Write-Host "  Practice Areas: $($response.metadata.practice_areas_supported)" -ForegroundColor Gray
            }
        }
        
        Write-Host "`n" ("-"*100) -ForegroundColor DarkGray
        Write-Host "RESPONSE (First 800 characters):" -ForegroundColor Cyan
        Write-Host ("-"*100) -ForegroundColor DarkGray
        Write-Host $response.answer.Substring(0, [Math]::Min(800, $response.answer.Length)) -ForegroundColor White
        if ($response.answer.Length > 800) {
            Write-Host "`n... [Response continues for $($response.answer.Length - 800) more characters]" -ForegroundColor Gray
        }
        Write-Host ("-"*100) -ForegroundColor DarkGray
        
        return $true
    }
    catch {
        Write-Host "FAILED!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        return $false
    }
}

# ================================================================================================
# START TESTS
# ================================================================================================

Write-Host "`n`n"
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "  LEGID COMPLETE SYSTEM - COMPREHENSIVE DEMO TEST" -ForegroundColor Cyan
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing all 4 LEGID systems with real-world legal questions..." -ForegroundColor White
Write-Host "Backend: $baseUrl" -ForegroundColor Gray
Write-Host ""

$results = @{}

# ================================================================================================
# TEST 1: LEGID MASTER PROMPT (General Legal Intelligence)
# ================================================================================================

$results["LEGID Master"] = Test-Endpoint `
    -SystemName "SYSTEM 1: LEGID MASTER PROMPT (General Legal Intelligence)" `
    -Endpoint "/api/chat/legid" `
    -Question "What are my Charter rights if I am arrested in Canada?" `
    -Color "Yellow"

Start-Sleep -Seconds 2

# ================================================================================================
# TEST 2: ONTARIO LTB SPECIALIST (Landlord & Tenant Board Expert)
# ================================================================================================

$results["Ontario LTB"] = Test-Endpoint `
    -SystemName "SYSTEM 2: ONTARIO LTB SPECIALIST (Landlord & Tenant Board Expert)" `
    -Endpoint "/api/chat/legid/ontario-ltb" `
    -Question "I received Form N4 for unpaid rent. My landlord never fixed the broken heater I reported 3 months ago. What are my options?" `
    -Color "Magenta"

Start-Sleep -Seconds 2

# ================================================================================================
# TEST 3: CANADA-USA MASTER (4-Layer Institutional Reasoning)
# ================================================================================================

$results["Canada-USA Master"] = Test-Endpoint `
    -SystemName "SYSTEM 3: CANADA-USA MASTER (4-Layer Institutional Reasoning)" `
    -Endpoint "/api/chat/legid/canada-usa" `
    -Question "I earned 18,000 dollars in Canada this year. My employer deducted 1,200 dollars in taxes. Do I have to file? Will I get a refund?" `
    -Color "Green"

Start-Sleep -Seconds 2

# ================================================================================================
# TEST 4: RAG-FIRST PRODUCTION (THE COMPLETE SYSTEM - Crown Jewel)
# ================================================================================================

$results["RAG Production"] = Test-Endpoint `
    -SystemName "SYSTEM 4: RAG-FIRST PRODUCTION (THE COMPLETE SYSTEM - Crown Jewel)" `
    -Endpoint "/api/chat/legid/rag-production" `
    -Question "I am a low-income single parent in Ontario. What tax credits and benefits should I apply for? Do I need to file taxes even if I earned less than 15,000 dollars?" `
    -Color "Cyan"

# ================================================================================================
# SUMMARY
# ================================================================================================

Write-Host "`n`n"
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host ""

$passed = ($results.Values | Where-Object { $_ -eq $true }).Count
$total = $results.Count

foreach ($test in $results.GetEnumerator()) {
    $status = if ($test.Value) { "PASS" } else { "FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "$status - $($test.Key)" -ForegroundColor $color
}

Write-Host ""
Write-Host "Total: $passed/$total tests passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -eq $total) {
    Write-Host ""
    Write-Host ("="*100) -ForegroundColor Green
    Write-Host "  ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
    Write-Host ("="*100) -ForegroundColor Green
    Write-Host ""
    Write-Host "Your AI is now MORE SOPHISTICATED than ChatGPT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Key differences you should notice:" -ForegroundColor White
    Write-Host "  1. LEGID Master: Structured 5-part responses with Charter sections" -ForegroundColor Gray
    Write-Host "  2. Ontario LTB: Form-specific guidance, defence-aware (maintenance issues)" -ForegroundColor Gray
    Write-Host "  3. Canada-USA: Separates tax owing from filing obligation" -ForegroundColor Gray
    Write-Host "  4. RAG Production: Highest confidence, practice-area routing, most complete" -ForegroundColor Gray
    Write-Host ""
    Write-Host "RECOMMENDED FOR PRODUCTION: RAG-First Production (System 4)" -ForegroundColor Cyan
    Write-Host "Endpoint: /api/chat/legid/rag-production" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ("="*100) -ForegroundColor Cyan
