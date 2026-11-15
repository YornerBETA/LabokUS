# Release layout

Use <version>/<platform>/<installer-language>/, e.g. 1.0.0/W/Russian/.
Platform codes: W=Windows, LX=Linux, MO=macOS, AND=Android (APK/AAB), iOS=iOS.
Keep platform installers separate. Windows builds must never offer Android APKs.
The stable release manifest is releases/stable.json. A future bootstrapper must verify HTTPS, SHA-256 and signed release metadata before installing; preserve rollback.