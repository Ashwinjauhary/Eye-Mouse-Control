; Eye Mouse Control Installer Script
; Requires NSIS (Nullsoft Scriptable Install System)

!define APPNAME "Eye Mouse Control"
!define COMPANYNAME "Eye Mouse Control Team"
!define DESCRIPTION "Hands-free mouse control using face tracking and blink detection"
!define HELPURL "https://github.com/example/eye-mouse-control/issues" ; Support URL
!define UPDATEURL "https://github.com/example/eye-mouse-control" ; Update URL
!define ABOUTURL "https://github.com/example/eye-mouse-control" ; About URL
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define VERSIONREVISION 0

; Define installation directory
!define INSTALLDIR "$PROGRAMFILES\${APPNAME}"

; Request admin permissions for installation
RequestExecutionLevel admin

; Modern UI interface
!include "MUI2.nsh"

; General settings
Name "${APPNAME}"
OutFile "EyeMouseControl_Setup_v${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"
Unicode True

; Default installation directory
InstallDir "${INSTALLDIR}"

; Get installation folder from registry if available
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "eye_mouse_control.ico"
!define MUI_UNICON "eye_mouse_control.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Core Files" SecCore
    
    SectionIn RO ; Required section
    
    ; Set output path to the installation directory
    SetOutPath $INSTDIR
    
    ; Main executable
    File "dist\EyeMouseControl.exe"
    
    ; Documentation
    File "README.md"
    File "INSTALL.txt"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Add/Remove Programs entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$INSTDIR\Uninstall.exe /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\EyeMouseControl.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.${VERSIONREVISION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\EyeMouseControl.exe" "" "$INSTDIR\EyeMouseControl.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\User Manual.lnk" "$INSTDIR\README.md" "" "$INSTDIR\README.md" 0
    
    ; Create Desktop shortcut
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\EyeMouseControl.exe" "" "$INSTDIR\EyeMouseControl.exe" 0
    
SectionEnd

Section "Start with Windows" SecAutoStart
    
    CreateShortCut "$SMSTARTUP\${APPNAME}.lnk" "$INSTDIR\EyeMouseControl.exe" "" "$INSTDIR\EyeMouseControl.exe" 0
    
SectionEnd

Section "Configuration Files" SecConfig
    
    SetOutPath "$APPDATA\${APPNAME}"
    
    ; Create default configuration if it doesn't exist
    IfFileExists "$APPDATA\${APPNAME}\calibration.json" SkipConfig
        FileOpen $0 "$APPDATA\${APPNAME}\calibration.json" w
        FileWrite $0 "{$\r$\n$\t$\t\"center_x\": 0.5,$\r$\n$\t$\t\"center_y\": 0.5,$\r$\n$\t$\t\"min_x\": 0.0,$\r$\n$\t$\t\"max_x\": 1.0,$\r$\n$\t$\t\"min_y\": 0.0,$\r$\n$\t$\t\"max_y\": 1.0,$\r$\n$\t$\t\"ear_threshold\": 0.21,$\r$\n$\t$\t\"ear_consecutive_frames\": 2,$\r$\n$\t$\t\"sensitivity_x\": 1.0,$\r$\n$\t$\t\"sensitivity_y\": 1.0,$\r$\n$\t$\t\"deadzone_px\": 8,$\r$\n$\t$\t\"smoothing_alpha\": 0.25$\r$\n}"
        FileClose $0
    SkipConfig:
    
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files and documentation"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} "Launch Eye Mouse Control automatically when Windows starts"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecConfig} "Create default configuration files in user data directory"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    
    ; Delete files
    Delete $INSTDIR\EyeMouseControl.exe
    Delete $INSTDIR\README.md
    Delete $INSTDIR\INSTALL.txt
    Delete $INSTDIR\Uninstall.exe
    
    ; Delete shortcuts
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\User Manual.lnk"
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMSTARTUP\${APPNAME}.lnk"
    
    ; Remove directories
    RMDir "$SMPROGRAMS\${APPNAME}"
    RMDir /r "$INSTDIR"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCU "Software\${APPNAME}"
    
SectionEnd

; Functions
Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APPNAME} is already installed. $\n$\nClick `OK` to remove the previous version or `Cancel` to cancel this upgrade." \
    IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
    
    done:
FunctionEnd
