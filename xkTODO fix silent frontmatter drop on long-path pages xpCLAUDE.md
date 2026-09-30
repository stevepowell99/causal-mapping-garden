# Silent bug: YAML front matter dropped on 85 over-length pages

Found 2026-08-31 while writing the QuIP pages. `build_static_site.py:7505-7514` reads each page's YAML front matter with a plain `p.read_text(encoding="utf-8")` inside a bare `except Exception`, which on failure silently sets `metadata_map[p] = {}` and swallows the error. Windows' 260-character path limit means this fails for any page whose absolute path is longer, and this Drive-mirrored repo has plenty.

On this machine (STEVE-DELL): **85 markdown pages exceed the limit; 69 of them are having their front matter silently dropped**, including 21 with a `theme:`, 7 `case_study`, 4 `paper` and 1 `dual-column`. The page still renders, just without its styling/theme/tag metadata, with no build warning.

The file already has a long-path-safe reader, `_read_text_windows_safe` (line ~220), used elsewhere (e.g. the bib parser, line ~255). Line 7509 just isn't calling it.

Two independent things, either fixable alone:

1. **Code fix (durable, works on any machine) — still open.** Swap `p.read_text(...)` for `_read_text_windows_safe(p, ...)` at line 7509, and make the `except Exception` branch call `_warn(...)` instead of silently swallowing, so a genuine future read failure is visible in the build output rather than a silent `{}`.
2. **Registry fix (this machine only, and only masks the symptom) — done 2026-08-31.** `LongPathsEnabled` is now `1` in `HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem` on STEVE-DELL (someone ran the elevated `Set-ItemProperty` below at some point between the two sessions). Confirmed live in a follow-up session: wrote and read back a 700-character path via pwsh 7, Python and `cmd /c dir`, all succeeded. `git config --get core.longpaths` was already `true` (unrelated setting, unaffected). So the registry-side blocker on this machine is cleared; this masks the symptom here but the ThinkPad or a rebuilt machine would still hit it silently, since git doesn't carry a registry value — no `machine-parity.ps1` row asserts it yet.
   ```
   Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -Type DWord
   ```

**Remaining work:** the code fix (item 1) is the durable one and is still needed so a rebuilt or replacement machine doesn't silently drop front matter again. Worth a `machine-parity.ps1` check for `LongPathsEnabled` too, since reading the registry value needs no elevation.
