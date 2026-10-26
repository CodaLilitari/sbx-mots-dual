# Run with Windows PowerShell 5.1 (System.Drawing / .NET Framework).
# The original PNG must be an exact 640x480 decode of SBX ui/bm/bkmain.bm.
param(
    [Parameter(Mandatory=$true)][string]$OriginalPng,
    [Parameter(Mandatory=$true)][string]$OutputPng,
    [string]$WordmarkPng = ''
)
if (-not $WordmarkPng) { $WordmarkPng = Join-Path $PSScriptRoot 'special-edition-wordmark.png' }
if (Test-Path -LiteralPath $OutputPng) { throw 'Choose a new output PNG; existing artwork is never overwritten.' }
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
public static class SbxTitleArt {
 public static string Compose(string original, string wordmark, string output) {
  using (var bg = new Bitmap(original))
  using (var text = new Bitmap(wordmark))
  using (var result = new Bitmap(640,480,PixelFormat.Format32bppArgb)) {
   int x0=text.Width,y0=text.Height,x1=-1,y1=-1;
   for(int y=0;y<text.Height;y++) for(int x=0;x<text.Width;x++) {
    if(text.GetPixel(x,y).A>=16) { x0=Math.Min(x0,x); y0=Math.Min(y0,y); x1=Math.Max(x1,x); y1=Math.Max(y1,y); }
   }
   if(x1<x0) throw new Exception("No visible wordmark");
   using(var g=Graphics.FromImage(result)) {
    g.CompositingMode=CompositingMode.SourceCopy;
    g.DrawImageUnscaled(bg,0,0);
    g.FillRectangle(Brushes.Black,450,0,166,97);
    g.DrawImage(bg,new Rectangle(450,0,166,80),new Rectangle(450,17,166,80),GraphicsUnit.Pixel);
    g.CompositingMode=CompositingMode.SourceOver;
    g.InterpolationMode=InterpolationMode.HighQualityBicubic;
    g.PixelOffsetMode=PixelOffsetMode.HighQuality;
    g.CompositingQuality=CompositingQuality.HighQuality;
    g.DrawImage(text,new Rectangle(463,80,140,14),new Rectangle(x0,y0,x1-x0+1,y1-y0+1),GraphicsUnit.Pixel);
   }
   result.Save(output,ImageFormat.Png);
   return String.Format("source={0}x{1};alpha_bounds={2},{3},{4},{5};wordmark_destination=463,80,140,14;logo_translation=0,-17",text.Width,text.Height,x0,y0,x1+1,y1+1);
  }
 }
}
'@
$composition = [SbxTitleArt]::Compose($OriginalPng,$WordmarkPng,$OutputPng)
[ordered]@{
    original_png_sha256=(Get-FileHash -LiteralPath $OriginalPng -Algorithm SHA256).Hash.ToLower()
    wordmark_sha256=(Get-FileHash -LiteralPath $WordmarkPng -Algorithm SHA256).Hash.ToLower()
    output_png_sha256=(Get-FileHash -LiteralPath $OutputPng -Algorithm SHA256).Hash.ToLower()
    composition=$composition
} | ConvertTo-Json | Set-Content -LiteralPath ($OutputPng + '.provenance.json') -Encoding utf8
$composition
