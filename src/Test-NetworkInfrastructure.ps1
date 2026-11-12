<#
.SYNOPSIS
    Tests network infrastructure connectivity: Default Gateway, DNS Resolution, and Active Directory DC ports.
    Testa conectividade de infraestrutura de rede: Gateway Padrão, DNS e portas de Controlador de Domínio (AD).
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$DomainController,

    [Parameter(Mandatory = $false)]
    [string]$TestDnsName = "github.com"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   NETWORK & ACTIVE DIRECTORY CONNECTIVITY DIAGNOSTICS" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Default Gateway Check
Write-Host "`n[1] DEFAULT GATEWAY CHECK" -ForegroundColor Yellow
$Gateways = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty NextHop -Unique
foreach ($Gw in $Gateways) {
    if ($Gw -and $Gw -ne "0.0.0.0") {
        $Ping = Test-Connection -ComputerName $Gw -Count 2 -Quiet -ErrorAction SilentlyContinue
        $Color = if ($Ping) { "Green" } else { "Red" }
        $State = if ($Ping) { "REACHABLE" } else { "UNREACHABLE" }
        Write-Host "    Gateway $Gw : $State" -ForegroundColor $Color
    }
}

# 2. DNS Resolution Check
Write-Host "`n[2] DNS RESOLUTION TEST ($TestDnsName)" -ForegroundColor Yellow
try {
    $DnsResult = Resolve-DnsName -Name $TestDnsName -Type A -ErrorAction Stop | Select-Object -First 3
    foreach ($Rec in $DnsResult) {
        Write-Host "    Resolved $($Rec.Name) -> $($Rec.IPAddress) [OK]" -ForegroundColor Green
    }
}
catch {
    Write-Host "    DNS Resolution failed for ${TestDnsName}: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Active Directory Domain Controller Port Verification
if (-not [string]::IsNullOrWhiteSpace($DomainController)) {
    Write-Host "`n[3] DOMAIN CONTROLLER PORT AUDIT ($DomainController)" -ForegroundColor Yellow
    $ADPorts = @(
        @{ Port = 53;   Service = "DNS" }
        @{ Port = 88;   Service = "Kerberos" }
        @{ Port = 135;  Service = "RPC Endpoint Mapper" }
        @{ Port = 389;  Service = "LDAP" }
        @{ Port = 445;  Service = "SMB / SYSVOL" }
        @{ Port = 636;  Service = "LDAPS" }
        @{ Port = 3268; Service = "Global Catalog" }
    )

    foreach ($Item in $ADPorts) {
        $TcpClient = New-Object System.Net.Sockets.TcpClient
        $Async = $TcpClient.BeginConnect($DomainController, $Item.Port, $null, $null)
        $Wait = $Async.AsyncWaitHandle.WaitOne(1500, $false)
        if ($Wait -and $TcpClient.Connected) {
            Write-Host ("    TCP {0,-5} ({1,-20}) : OPEN" -f $Item.Port, $Item.Service) -ForegroundColor Green
        } else {
            Write-Host ("    TCP {0,-5} ({1,-20}) : CLOSED / FILTERED" -f $Item.Port, $Item.Service) -ForegroundColor Red
        }
        $TcpClient.Close()
    }
}
