; Inno Setup Script para Auto NFe
; Criado para criar um instalador Windows com atalho no Menu Iniciar

#define MyAppName "Auto NFe"
; Versão é passada via linha de comando pelo build_installer.ps1
#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif
#define MyAppPublisher "Andre Grassi de Jesus"
#define MyAppExeName "auto_nfe_app.exe"
#define MyAppCopyright "Copyright (C) 2026 by Andre Grassi de Jesus"

[Setup]
; Identificador único do aplicativo (gere um novo GUID em https://www.guidgenerator.com/)
AppId={{978d3c1f-126e-4e37-be98-5ff83d99759e}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright={#MyAppCopyright}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Permite que o usuário escolha criar atalho na área de trabalho
AllowNoIcons=yes
; Caminho de saída do instalador
OutputDir=output
OutputBaseFilename=AutoNFe_Setup_{#MyAppVersion}
; Ícone do instalador (opcional - descomente e ajuste o caminho se tiver um ícone)
; SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Privilegios de admin para instalação de pré-requisitos se necessário
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia todos os arquivos do build para o diretório de instalação
Source: "..\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Pré-requisitos (WebView2 e VC++ Redistributable)
Source: "prerequisites\MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall
Source: "prerequisites\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall

[Icons]
; Atalho no Menu Iniciar
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Atalho para desinstalar no Menu Iniciar
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
; Atalho na Área de Trabalho (se selecionado)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Instala WebView2 se não estiver presente (necessário para Flet)
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; StatusMsg: "Instalando Microsoft Edge WebView2 Runtime..."; Check: not IsWebView2Installed; Flags: waituntilterminated

; Instala Visual C++ Redistributable se não estiver presente
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando Visual C++ Redistributable..."; Check: not IsVCRedistInstalled; Flags: waituntilterminated

; Opção para executar o app após a instalação
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Verifica se WebView2 Runtime está instalado
function IsWebView2Installed: Boolean;
var
  Version: string;
begin
  Result := RegQueryStringValue(HKEY_LOCAL_MACHINE, 
    'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 
    'pv', Version) or
    RegQueryStringValue(HKEY_CURRENT_USER, 
    'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 
    'pv', Version);
end;

// Verifica se Visual C++ Redistributable 2015-2022 está instalado
function IsVCRedistInstalled: Boolean;
begin
  Result := RegKeyExists(HKEY_LOCAL_MACHINE, 
    'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') or
    RegKeyExists(HKEY_LOCAL_MACHINE, 
    'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
end;
