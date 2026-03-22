param(
    [string]$BaseUrl = "http://localhost:8000/public/report/export",
    [string]$BigFile = "big.txt",
    [string]$SmallFile = "min.txt"
)

# Проверка наличия маленького файла
if (-not (Test-Path $SmallFile)) {
    "dummy content" | Out-File $SmallFile -Encoding ascii
    Write-Host "Created $SmallFile with dummy content" -ForegroundColor Yellow
}

# Проверка наличия большого файла
if (-not (Test-Path $BigFile)) {
    Write-Host "ERROR: Big file $BigFile not found. Please create a 500MB file (e.g., using fsutil)." -ForegroundColor Red
    exit 1
}

$jobs = @(
    @{ Name = "Big1";  File = $BigFile;   Size = "500MB" },
    @{ Name = "Big2";  File = $BigFile;   Size = "500MB" },
    @{ Name = "Small1"; File = $SmallFile; Size = "small" },
    @{ Name = "Small2"; File = $SmallFile; Size = "small" }
)

Write-Host "`n=== Starting 4 parallel uploads ===" -ForegroundColor Cyan
$total = $jobs.Count
$current = 0

# Локальные копии для параллельного блока
$baseUrlLocal = $BaseUrl

$results = $jobs | ForEach-Object -Parallel {
    $job = $_
    $url = $using:baseUrlLocal
    $file = $job.File
    $name = $job.Name
    $size = $job.Size

    # Информирование о старте
    Write-Host "[$name] Uploading $size file..." -ForegroundColor Magenta

    # Замеры времени
    $startTime = Get-Date

    # Выполнение запроса
    $response = curl.exe -s -X POST $url -F "file=@$file"

    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds

    try {
        $obj = $response | ConvertFrom-Json
        $status = $obj.status
        $taskId = $obj.task_id

        # Сразу выводим результат
        Write-Host "[$name] Response: Status=$status, TaskId=$taskId (took $([math]::Round($duration,2))s)" -ForegroundColor Green

        [PSCustomObject]@{
            JobName = $name
            Status  = $status
            TaskId  = $taskId
            Duration = $duration
        }
    } catch {
        Write-Host "[$name] ERROR: Failed to parse response: $response" -ForegroundColor Red
        [PSCustomObject]@{
            JobName = $name
            Status  = "error"
            TaskId  = $null
            Duration = $duration
            Raw     = $response
        }
    }
} -ThrottleLimit 4

Write-Host "`n=== Summary of uploads ===" -ForegroundColor Cyan
$results | Format-Table JobName, Status, TaskId, @{Name="Time(s)"; Expression={[math]::Round($_.Duration,2)}} -AutoSize

# Сохранение успешных task_id в файл
$successIds = $results | Where-Object { $_.TaskId } | Select-Object -ExpandProperty TaskId
if ($successIds) {
    $successIds | Out-File -FilePath "task_ids.txt" -Encoding ascii
    Write-Host "Task IDs saved to task_ids.txt ($($successIds.Count) IDs)" -ForegroundColor Yellow
} else {
    Write-Host "No successful uploads to save." -ForegroundColor Red
}