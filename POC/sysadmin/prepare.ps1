## Powershell Command file
$BINDIR = 'bin'
$GITDIR = 'git'
$path = pwd

$yeah = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes","Description."
$nah = New-Object System.Management.Automation.Host.ChoiceDescription "&No","Description."
$abort = New-Object System.Management.Automation.Host.ChoiceDescription "&Cancel","Description."
$options = [System.Management.Automation.Host.ChoiceDescription[]]($yeah, $nah, $abort)
$heading = "Install Python3"
$mess = "Do you want to download and install PYthon 3"
$rslt = $host.ui.PromptForChoice($heading, $mess, $options, 1)
if ($rslt -eq  0) {
    echo "Downloading Python and running the installer" 
    wget https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe -o python-3.11.7-amd64.exe 
   .\python-3.11.7-amd64.exe
}

echo "Installing pyyaml" 
pip3 install pyyaml

if (!(Test-Path $path/$GITDIR/bin/git.exe -PathType Leaf)) 
{ 
   echo "Downloading a portable version of git" 
   wget  https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe -o PortableGit-2.43.0-64-bit.7z.exe
  ./PortableGit-2.43.0-64-bit.7z.exe  -o $path/$GITDIR -y
}

$getRclone = 0 
if (!(Test-Path $BINDIR/rclone.exe -PathType Leaf)) { $getRclone = 1 } 
if ($getRclone -eq 0) {
    $heading = "Update Rclone"
    $mess = "Do you want to update Rclone to the latest version?"
    $rslt = $host.ui.PromptForChoice($heading, $mess, $options, 1)
    if ($rslt -eq 0) { $getRclone = 1 }
}

if ($getRclone -eq 1) {
     echo "Downloading rclone and unpacking in to $BINDIR"
     wget https://downloads.rclone.org/rclone-current-windows-amd64.zip -o rclone-current-windows-amd64.zip
     Expand-Archive -force -path .\rclone-current-windows-amd64.zip -destinationpath $BINDIR 

     $rclonedir = (Get-ChildItem $path/$BINDIR -Filter 'rclone*' -Directory | Sort-Object LastWriteTime | Select-Object -Last 1).FullName
     copy $rclonedir/*exe $BINDIR
}
if (!(Test-Path rcs3 -PathType Container)) { 
    echo "Cloning RCS3 git repository"
    ./git/bin/git clone https://github.com/RCIC-UCI-Public/rcs3.git
}
