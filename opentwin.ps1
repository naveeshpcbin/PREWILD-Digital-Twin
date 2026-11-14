<#
.SYNOPSIS
    PRW-Wild Digital Twin — Quick Launcher & Shortest Terminal View.
.DESCRIPTION
    Ensures background web server is active on port 8000, opens the digital twin
    website in your default browser in shortest view, and outputs the ultra-compact,
    shortest version of the digital twin status and hardware telemetry directly in
    the Windows Terminal.
.PARAMETER Watch
    Continuously watch real-time sensor updates in the terminal (alias: -Live).
.PARAMETER Live
    Continuously watch real-time sensor updates in the terminal.
.PARAMETER NoOpen
    Display shortest terminal view without launching the browser window.
.PARAMETER Full
    Open the digital twin website in full standard view instead of shortest view.
.PARAMETER Port
    Server port (default: 8000).
.EXAMPLE
    opentwin
.EXAMPLE
    opentwin -Watch
.EXAMPLE
    opentwin -Full
#>
param(
    [switch]$Watch,
    [switch]$Live,
    [switch]$NoOpen,
    [switch]$Full,
    [int]$Port = 8000
)

$cliArgs = @()
if ($Watch -or $Live) { $cliArgs += "--watch" }
if ($NoOpen) { $cliArgs += "--no-open" }
if ($Full) { $cliArgs += "--full" }
if ($Port -ne 8000) { $cliArgs += "--port"; $cliArgs += $Port }

$scriptPath = "D:\Simulation For DT\prw-wild-digital-twin\tools\opentwin.py"
$venvPy = "D:\Simulation For DT\venv\Scripts\python.exe"

if (Test-Path $venvPy) {
    & $venvPy $scriptPath @cliArgs
} else {
    python $scriptPath @cliArgs
}
