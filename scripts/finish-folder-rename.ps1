# Remove leftover C:\Users\ahmed\my-project after migrating to khukra.
# Run after closing Cursor if normal delete fails.

$old = "C:\Users\ahmed\my-project"
if (-not (Test-Path $old)) {
    Write-Host "Nothing to clean up: $old does not exist."
    exit 0
}

Write-Host "Removing leftover folder: $old"
Remove-Item -LiteralPath $old -Recurse -Force -ErrorAction SilentlyContinue
if (-not (Test-Path $old)) {
    Write-Host "Done. Project path: C:\Users\ahmed\khukra"
    exit 0
}

Write-Host "Some paths are locked. Scheduling delete on next reboot..."
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
  public static extern bool MoveFileEx(string lpExistingFileName, string lpNewFileName, int dwFlags);
}
"@
$MOVEFILE_DELAY_UNTIL_REBOOT = 4
$stack = New-Object System.Collections.Stack
$stack.Push($old)
while ($stack.Count -gt 0) {
    $current = $stack.Pop()
    Get-ChildItem -LiteralPath $current -Force -ErrorAction SilentlyContinue | ForEach-Object { $stack.Push($_.FullName) }
    [void][Win32]::MoveFileEx($current, $null, $MOVEFILE_DELAY_UNTIL_REBOOT)
}
Write-Host "Scheduled. Reboot Windows, or close Cursor and run this script again."
