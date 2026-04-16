$headers = @{
    "apikey" = "sb_publishable_ZF3uREWZRRqZpfV-zykABw_W802i9ig"
    "Content-Type" = "application/json"
}

try {
    $r = Invoke-RestMethod -Uri "https://pkhlytcqjgspkmsmzxpg.supabase.co/rest/v1/users?select=id,email,created_at&email=eq.test_fix_2026@example.com" -Method Get -Headers $headers
    Write-Host "=== 查询结果 ==="
    $r | ConvertTo-Json -Depth 5
} catch {
    Write-Host "=== 查询失败 ==="
    Write-Host "StatusCode:" $_.Exception.Response.StatusCode
    $stream = $_.Exception.Response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    Write-Host "Response:" $reader.ReadToEnd()
}
