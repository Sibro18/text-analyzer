param(
    [string]$BaseUrl = "http://localhost:8000/public/report/result",
    [string]$OutputDir = ".",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$TaskIds
)

if ($TaskIds.Count -eq 0) {
    if (Test-Path "task_ids.txt") {
        $TaskIds = Get-Content "task_ids.txt" | Where-Object { $_ -match '\S' }
        Write-Host "Loaded $($TaskIds.Count) task IDs from task_ids.txt" -ForegroundColor Cyan
    } else {
        Write-Host "No task IDs provided and task_ids.txt not found." -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created output directory: $OutputDir" -ForegroundColor Cyan
}

Write-Host "Downloading results for $($TaskIds.Count) tasks..." -ForegroundColor Cyan

$baseUrlLocal = $BaseUrl
$outputDirLocal = $OutputDir

$results = $TaskIds | ForEach-Object -Parallel {
    $id = $_
    $url = "$($using:baseUrlLocal)/$id"
    $outFile = Join-Path $using:outputDirLocal "result_$id.xlsx"
    
    $tempFile = [System.IO.Path]::GetTempFileName()
    $httpCode = curl.exe -s -L -X GET $url --write-out "%{http_code}" -o $tempFile 2>$null
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0 -and $httpCode -eq 200) {
        # Проверяем, не является ли содержимое JSON-статусом
        $content = Get-Content -Path $tempFile -Raw -Encoding utf8 -ErrorAction SilentlyContinue
        if ($content -match '^\s*\{.*\status.*\}\s*$' -or ($content -match '"status"')) {
            try {
                $obj = $content | ConvertFrom-Json
                if ($obj.PSObject.Properties.Name -contains 'status') {
                    # Это статус – удаляем временный файл и отображаем статус
                    Remove-Item -Path $tempFile -Force
                    [PSCustomObject]@{
                        TaskId = $id
                        Status = $obj.status
                        File   = $null
                        SizeKB = $null
                    }
                } else {
                    # Неизвестный JSON – возможно, ошибка
                    Remove-Item -Path $tempFile -Force
                    [PSCustomObject]@{
                        TaskId = $id
                        Status = "unknown JSON"
                        File   = $null
                        SizeKB = $null
                    }
                }
            } catch {
                # Ошибка парсинга – вероятно, это битый файл или не JSON
                Move-Item -Path $tempFile -Destination $outFile -Force
                $size = (Get-Item $outFile).Length
                [PSCustomObject]@{
                    TaskId = $id
                    Status = "downloaded (invalid JSON?)"
                    File   = $outFile
                    SizeKB = [math]::Round($size / 1KB, 2)
                }
            }
        } else {
            # Скорее всего, это настоящий Excel-файл
            Move-Item -Path $tempFile -Destination $outFile -Force
            $size = (Get-Item $outFile).Length
            [PSCustomObject]@{
                TaskId = $id
                Status = "downloaded"
                File   = $outFile
                SizeKB = [math]::Round($size / 1KB, 2)
            }
        }
    } else {
        # Ошибка HTTP или curl
        $content = Get-Content -Path $tempFile -Raw -Encoding utf8 -ErrorAction SilentlyContinue
        Remove-Item -Path $tempFile -Force
        try {
            $obj = $content | ConvertFrom-Json
            if ($obj.PSObject.Properties.Name -contains 'status') {
                [PSCustomObject]@{
                    TaskId = $id
                    Status = $obj.status
                    File   = $null
                    SizeKB = $null
                }
            } else {
                [PSCustomObject]@{
                    TaskId = $id
                    Status = "HTTP $httpCode, curl exit $exitCode, response: $content"
                    File   = $null
                    SizeKB = $null
                }
            }
        } catch {
            [PSCustomObject]@{
                TaskId = $id
                Status = "HTTP $httpCode, curl exit $exitCode, response: $content"
                File   = $null
                SizeKB = $null
            }
        }
    }
} -ThrottleLimit 4

Write-Host "`nDownload results:" -ForegroundColor Green
$results | Format-Table TaskId, Status, File, SizeKB -AutoSize