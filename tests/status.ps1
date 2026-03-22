param(
    [string]$BaseUrl = "http://localhost:8000/public/report/status",
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$TaskIds
)

if ($TaskIds.Count -eq 0) {
    if (Test-Path "task_ids.txt") {
        $TaskIds = Get-Content "task_ids.txt" | Where-Object { $_ -match '\S' }
    } else {
        Write-Host "No task IDs provided and task_ids.txt not found." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Checking status for $($TaskIds.Count) tasks..." -ForegroundColor Cyan
$baseUrlLocal = $BaseUrl

$statuses = $TaskIds | ForEach-Object -Parallel {
    $id = $_
    $url = "$($using:baseUrlLocal)/$id"
    
    # Выполняем curl тихо, но сохраняем вывод
    $response = curl.exe -s -X GET $url 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        [PSCustomObject]@{
            TaskId = $id
            Status = "curl error (exit $exitCode)"
        }
    } elseif ([string]::IsNullOrWhiteSpace($response)) {
        [PSCustomObject]@{
            TaskId = $id
            Status = "empty response"
        }
    } else {
        try {
            $obj = $response | ConvertFrom-Json
            [PSCustomObject]@{
                TaskId = $id
                Status = if ($obj.PSObject.Properties.Name -contains 'status') { $obj.status } else { "unknown" }
            }
        } catch {
            # Выводим фрагмент ответа для понимания
            $preview = $response.Substring(0, [Math]::Min(150, $response.Length))
            [PSCustomObject]@{
                TaskId = $id
                Status = "JSON error: $preview..."
            }
        }
    }
} -ThrottleLimit 5

Write-Host "`nTask statuses:" -ForegroundColor Green
$statuses | Format-Table TaskId, Status -AutoSize