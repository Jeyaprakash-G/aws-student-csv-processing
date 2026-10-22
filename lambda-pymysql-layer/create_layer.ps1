```powershell
$LayerPath = "C:\lambda-rds-project\layer\python"

New-Item -ItemType Directory -Path $LayerPath -Force

py -m pip install PyMySQL==1.2.3 --target $LayerPath

Compress-Archive -Path $LayerPath -DestinationPath "C:\lambda-rds-project\devops-pymysql-layer.zip" -Force
```
