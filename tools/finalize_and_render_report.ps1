# PRW-Wild Mini Project Report - Final Table of Contents & PDF Renderer
$ErrorActionPreference = "Stop"

$docxPath = "D:\Simulation For DT\prw-wild-digital-twin\report\PRW_WILD_MINI_PROJECT_FINAL\PRW_WILD_MINI_PROJECT_REPORT.docx"
$pdfPath = "D:\Simulation For DT\prw-wild-digital-twin\report\PRW_WILD_MINI_PROJECT_FINAL\PRW_WILD_MINI_PROJECT_REPORT.pdf"

Write-Host "[1/4] Starting Microsoft Word COM Object..." -ForegroundColor Cyan
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone

try {
    Write-Host "[2/4] Opening generated report document..." -ForegroundColor Cyan
    $doc = $word.Documents.Open($docxPath, $false, $false)
    $doc.Repaginate()

    $pageMappings = @(
        @{ Row = 2; Chapter = "CHAPTER 1 — INTRODUCTION"; Page = 5 },
        @{ Row = 3; Chapter = "CHAPTER 2 — LITERATURE SURVEY"; Page = 10 },
        @{ Row = 4; Chapter = "CHAPTER 3 — PROBLEM STATEMENT AND OBJECTIVES"; Page = 15 },
        @{ Row = 5; Chapter = "CHAPTER 4 — STAKEHOLDER PROFILES: PERSONA AND REQUIREMENTS"; Page = 17 },
        @{ Row = 6; Chapter = "CHAPTER 5 — METHODOLOGIES TO SOLVE THE PROBLEM — ANALYSIS"; Page = 22 },
        @{ Row = 7; Chapter = "CHAPTER 6 — APPLICATION OF ENGINEERING KNOWLEDGE / APPLICATION AREAS OF YOUR PROPOSED IDEA"; Page = 30 },
        @{ Row = 8; Chapter = "CHAPTER 7 — CONCEPTUAL DESIGN AND PROTOTYPE"; Page = 33 },
        @{ Row = 9; Chapter = "CHAPTER 8 — OUTCOME, SOCIETAL RELEVANCE AND FEEDBACK FROM CUSTOMERS AND STAKEHOLDERS TO REDESIGN"; Page = 36 },
        @{ Row = 10; Chapter = "CHAPTER 9 — CONTRIBUTION OF THE TEAM MEMBERS"; Page = 39 },
        @{ Row = 11; Chapter = "CHAPTER 10 — PROFESSIONAL ETHICS FOLLOWED"; Page = 41 },
        @{ Row = 12; Chapter = "CHAPTER 11 — CONCLUSION AND FUTURE WORK"; Page = 44 },
        @{ Row = 13; Chapter = "CHAPTER 12 — REFERENCES"; Page = 46 },
        @{ Row = 14; Chapter = "CHAPTER 13 — PLAGIARISM REPORT"; Page = 48 }
    )

    Write-Host "[3/4] Updating Table of Contents Table with authoritative page numbers..." -ForegroundColor Cyan
    $tocTable = $doc.Tables.Item(2)

    foreach ($item in $pageMappings) {
        $cell = $tocTable.Cell($item.Row, 3)
        $cell.Range.Text = "$($item.Page)"
        $cell.Range.Font.Name = "Times New Roman"
        $cell.Range.Font.Size = 11
        $cell.Range.Font.Bold = $false
        $cell.Range.ParagraphFormat.Alignment = 1 # Center
    }

    $doc.Repaginate()
    $doc.Save()
    Write-Host "  -> DOCX updated and saved successfully!" -ForegroundColor Green

    Write-Host "[4/4] Exporting to native PDF format..." -ForegroundColor Cyan
    # wdExportFormatPDF = 17
    # OptimizeFor = wdExportOptimizeForPrint (0)
    $doc.ExportAsFixedFormat(
        $pdfPath,
        17,     # wdExportFormatPDF
        $false, # OpenAfterExport
        0,      # wdExportOptimizeForPrint
        0,      # wdExportAllDocument
        1,      # From
        1,      # To
        0,      # wdExportDocumentContent
        $true,  # IncludeDocProps
        $true,  # KeepIRM
        0,      # wdExportCreateNoBookmarks
        $true,  # DocStructureTags
        $true,  # BitmapMissingFonts
        $false  # UseISO19005_1
    )
    Write-Host "  -> PDF successfully exported to: $pdfPath" -ForegroundColor Green

} finally {
    if ($doc) {
        $doc.Close([Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
    }
    $word.Quit()
}

Write-Host "Verification of generated artifacts:" -ForegroundColor Yellow
Get-Item $docxPath | Select-Object Name, Length, LastWriteTime
Get-Item $pdfPath | Select-Object Name, Length, LastWriteTime

