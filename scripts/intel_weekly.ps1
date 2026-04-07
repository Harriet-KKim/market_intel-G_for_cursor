# Windows 작업 스케줄러용: 주간 전략 리포트
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location (Join-Path $Root "pipeline")
py -3 -m pip install -r requirements.txt -q
py -3 -m intel_pipeline weekly
