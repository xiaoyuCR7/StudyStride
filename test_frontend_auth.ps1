$body = @{
    email = "test_frontend_2026@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$headers = @{
    "apikey" = "sb_publishable_ZF3uREWZRRqZpfV-zykABw_W802i9ig"
    "Content-Type" = "application/json"
}

try {
    $r = Invoke-RestMethod -Uri "https://pkhlytcqjgspkmsmzxpg.supabase.co/auth/v1/signup" -Method Post -Body $body -Headers $headers
    Write-Host "=== 注册成功 ==="
    $r | ConvertTo-Json -Depth 5
} catch {
    Write-Host "=== 注册失败 ==="
    Write-Host "StatusCode:" $_.Exception.Response.StatusCode
    $stream = $_.Exception.Response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Response:" $reader.ReadToEnd()
}
