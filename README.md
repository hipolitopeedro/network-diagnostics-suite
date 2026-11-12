# Network Diagnostics & Infrastructure Testing Suite

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
![Networking](https://img.shields.io/badge/Networking%20%26%20TCP%2FIP-1BA0D7?style=for-the-badge&logo=cisco&logoColor=white)

> **English:** Cross-platform network diagnostics toolkit built with **Python** and **PowerShell** for IT infrastructure troubleshooting: concurrent TCP port scanning (DNS, LDAP, Kerberos, SMB, RDP, SSH, HTTPS), DNS resolution verification, and Active Directory Domain Controller connectivity checks.
>
> **Português:** Ferramentas de diagnóstico de rede multiplataforma em **Python** e **PowerShell** para troubleshooting de infraestrutura de TI: verificação concorrente de portas TCP (DNS, LDAP, Kerberos, SMB, RDP, SSH, HTTPS), testes de resolução DNS e validação de conectividade com Controladores de Domínio (AD).

---

## Included Tools / Ferramentas Inclusas

| File | Description (EN) | Descrição (PT-BR) |
| :--- | :--- | :--- |
| [`src/network_scanner.py`](src/network_scanner.py) | Zero-dependency Python CLI tool using `socket` and `concurrent.futures` to test host reachability, measure TCP handshake latency (ms), verify DNS records, and export JSON reports. | Utilitário CLI em Python (sem dependências externas) que testa conectividade, mede latência TCP em milissegundos, valida resolução DNS e exporta relatórios JSON. |
| [`src/Test-NetworkInfrastructure.ps1`](src/Test-NetworkInfrastructure.ps1) | PowerShell script to validate default gateways, DNS servers, and Active Directory Domain Controller ports (`53`, `88`, `135`, `389`, `445`, `636`, `3268`). | Script PowerShell para validar gateways padrão, servidores DNS e portas essenciais de Controladores de Domínio do Active Directory. |

---

## Usage Examples / Exemplos de Uso

### 1. Python Infrastructure Scanner (`network_scanner.py`)
```bash
# Scan common infrastructure ports on target hosts and export JSON report
python src/network_scanner.py --hosts 1.1.1.1 8.8.8.8 --ports 53 80 443 --output report.json

# Scan default infrastructure profile (SSH, DNS, HTTP, Kerberos, LDAP, HTTPS, SMB, RDP)
python src/network_scanner.py --hosts dc01.corp.local fileserver.corp.local
```

### 2. PowerShell AD & Network Connectivity Check (`Test-NetworkInfrastructure.ps1`)
```powershell
# Test local gateway, DNS, and verify Active Directory ports on a Domain Controller
.\src\Test-NetworkInfrastructure.ps1 -DomainController "dc01.corp.local" -TestDnsName "github.com"
```
