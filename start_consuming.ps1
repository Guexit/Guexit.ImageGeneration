if(Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if($_ -notmatch '^#') {
            $key, $value = $_ -split '=', 2
            $value = $value -replace ',,', ','
            [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            Write-Output "$key=$value"
        }
    }
}

python .\services\image_generation_message_handler.py
