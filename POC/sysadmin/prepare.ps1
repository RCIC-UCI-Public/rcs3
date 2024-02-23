## Powershell Command file
# This file will download prerequisites for RCS3 into the current directory
#       * python3
#       * get-pip.py
#       * pip
#       * pyyaml
#       * rclone
#       * git
#
# it will then clone the rcs3 repository
# Typical usage:
#     mkdir \backup
#     cd \backup
#     wget https://raw.githubusercontent.com/RCIC-UCI-Public/rcs3/main/POC/sysadmin/prepare.ps1 -o prepare.ps1
#     ./prepare.ps1
#
$BINDIR = 'bin'
$GITDIR = 'git'
$path = pwd

$PYTHON_EMBED = 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip'
$PYTHON_MINOR = 11
$PYDIR = "python3$PYTHON_MINOR"
$GETPIP = "https://bootstrap.pypa.io/get-pip.py"

if (!(Test-Path $path/$PYDIR/python.exe -PathType Leaf)) 
{ 
   echo "Downloading a embedded version of python3" 
   wget  $PYTHON_EMBED -o python3$PYTHON_MINOR.zip 
   Expand-Archive python3$PYTHON_MINOR.zip -DestinationPath $PYDIR
   echo "Setting up to make pip available"
   wget $GETPIP -o get-pip.py
   & $PYDIR\python.exe get-pip.py --no-warn-script-location
   echo "Setting up $PYDIR\$PYDIR._pth"
   Add-Content -Path $PYDIR\$PYDIR._pth -Value "./Lib/site-packages"
   echo "installing pyyaml"
   & $PYDIR\python.exe -m pip install pyyaml 
}


if (!(Test-Path $path/$GITDIR/bin/git.exe -PathType Leaf)) 
{ 
   echo "Downloading a portable version of git" 
   wget  https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe -o PortableGit-2.43.0-64-bit.7z.exe
  ./PortableGit-2.43.0-64-bit.7z.exe  -o $path/$GITDIR -y
}

# Prompt if the user wants an updated version of rclone
$yeah = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes","Description."
$nah = New-Object System.Management.Automation.Host.ChoiceDescription "&No","Description."
$abort = New-Object System.Management.Automation.Host.ChoiceDescription "&Cancel","Description."
$options = [System.Management.Automation.Host.ChoiceDescription[]]($yeah, $nah, $abort)
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

# Clone RCS3 repo if not already there
if (!(Test-Path rcs3 -PathType Container)) { 
    echo "Cloning RCS3 git repository"
    ./git/bin/git clone https://github.com/RCIC-UCI-Public/rcs3.git
}
