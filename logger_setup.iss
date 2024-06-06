; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a x64 edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!
#define   Name       "Logger configurator"
#define   Version    "1.0.8"
#define   Publisher  "KAPTAR TECHNOLOGIES"
#define   URL        "https://kaptar.io/"
#define   ExeName    "Logger.exe"
#define   SourcePath "build\Logger configurator"

[Setup]
AppId={{02A76DD5-CBE8-4B1E-B48B-BC68C617E27E}
AppName={#Name}
AppVersion={#Version}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}
PrivilegesRequired=admin
WizardStyle=modern
DefaultDirName={autopf}\{#Publisher}\{#Name}
DefaultGroupName={#Publisher}
UsePreviousAppDir=no
SetupIconFile="{#SourcePath}\icons\icon.ico"
UninstallDisplayIcon="{#SourcePath}\icons\uninstall.ico"

Compression=lzma2
SolidCompression=yes
OutputDir="SetupFile"
OutputBaseFilename="LoggerConfiguratorSetup"
; ArchitecturesAllowed=x64 specifies that Setup cannot run on
; anything but x64.
ArchitecturesAllowed=x64
; ArchitecturesInstallIn64BitMode=x64 requests that the install be
; done in 64-bit mode on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "{#SourcePath}\*"; DestDir: {app};
Source: "{#SourcePath}\icons\*"; DestDir: {app}\icons;
Source: "{#SourcePath}\lib\*"; DestDir: {app}\lib; Flags: ignoreversion recursesubdirs
Source: "TermsAndConditions.txt"; Flags: dontcopy

;[Icons]
;Name {group}My Program; Filename {app}MyProg.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Icons]
Name: "{userdesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; IconFilename: "{app}\icons\icon.ico"; Tasks: desktopicon


[Code]

var
  SecondLicensePage: TOutputMsgMemoWizardPage;
  License2AcceptedRadio: TRadioButton;
  License2NotAcceptedRadio: TRadioButton;

procedure CheckLicense2Accepted(Sender: TObject);
begin
  // Update Next button when user (un)accepts the license
  WizardForm.NextButton.Enabled := License2AcceptedRadio.Checked;
end;

function CloneLicenseRadioButton(Source: TRadioButton): TRadioButton;
begin
  Result := TRadioButton.Create(WizardForm);
  Result.Parent := SecondLicensePage.Surface;
  Result.Caption := Source.Caption;
  Result.Left := Source.Left;
  Result.Top := Source.Top;
  Result.Width := Source.Width;
  Result.Height := Source.Height;
  // Needed for WizardStyle=modern / WizardResizable=yes
  Result.Anchors := Source.Anchors;
  Result.OnClick := @CheckLicense2Accepted;
end;

procedure InitializeWizard();
var
  LicenseFileName: string;
  LicenseFilePath: string;
begin
  // Create second license page, with the same labels as the original license page
  SecondLicensePage :=
    CreateOutputMsgMemoPage(
      wpLicense, SetupMessage(msgWizardLicense), SetupMessage(msgLicenseLabel),
      SetupMessage(msgLicenseLabel3), '');

  // Shrink license box to make space for radio buttons
  SecondLicensePage.RichEditViewer.Height := WizardForm.LicenseMemo.Height;

  // Load license
  // Loading ex-post, as Lines.LoadFromFile supports UTF-8,
  // contrary to LoadStringFromFile.
  LicenseFileName := 'TermsAndConditions.txt';
  ExtractTemporaryFile(LicenseFileName);
  LicenseFilePath := ExpandConstant('{tmp}\' + LicenseFileName);
  SecondLicensePage.RichEditViewer.Lines.LoadFromFile(LicenseFilePath);
  DeleteFile(LicenseFilePath);

  // Clone accept/do not accept radio buttons for the second license
  License2AcceptedRadio :=
    CloneLicenseRadioButton(WizardForm.LicenseAcceptedRadio);
  License2NotAcceptedRadio :=
    CloneLicenseRadioButton(WizardForm.LicenseNotAcceptedRadio);

  // Initially not accepted
  License2NotAcceptedRadio.Checked := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  // Update Next button when user gets to second license page
  if CurPageID = SecondLicensePage.ID then
  begin
    CheckLicense2Accepted(nil);
  end;
end;
