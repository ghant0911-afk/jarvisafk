$url = "https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF/resolve/main/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf"
$dest = "C:\Users\bear_\.gemini\antigravity\scratch\JarvisUltra_Flash\LocalModel\hermes.gguf"
$max_retries = 100
$retry_count = 0
while ($retry_count -lt $max_retries) {
    Write-Host "Попытка $($retry_count + 1) скачивания Hermes..."
    curl.exe -L -C - -o $dest $url
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ЗАГРУЗКА УСПЕШНО ЗАВЕРШЕНА!"
        break
    }
    Write-Host "Обрыв связи. Повтор через 5 секунд..."
    Start-Sleep -Seconds 5
    $retry_count++
}