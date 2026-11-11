# DocRevisor

Portable Windows PDF workspace, built from the open-source [storytold/pdfcraft](https://github.com/storytold/pdfcraft) **v0.19.0** source distribution. This is an independent derivative, not an official upstream release.

## Build on GitHub (no Windows or Rust installation required)

Open [Actions → DocRevisor Windows Portable](https://github.com/eftee/DocRevisor/actions/workflows/windows-portable.yml) and select **Run workflow**. The workflow also runs on updates to `main`. If compilation succeeds, download the `DocRevisor-Windows-Portable` artifact, extract it, and run `DocRevisor.exe` on a Windows device where execution is permitted.

The build fetches upstream source, applies `rebrand.py` to the Rust workspace and associated text/resources, compiles the GUI/CLI on a GitHub-hosted Windows runner, checks the Windows ProductName and produces a portable ZIP.

## Verification status

Repository and build recipe created. An actual successful Windows build and application-level regression testing must be verified from GitHub Actions. A source rename audit is not proof that every binary string or dependency has been completely rebranded. Icons inherited from upstream may still resemble their original branding, and source provenance and legal notices must remain.

## Licenses and safety

The upstream project is licensed MIT OR Apache-2.0. Preserve relevant original license and attribution notices; do not claim the derivative is original or official. This is unsigned software. Being portable does **not** bypass Windows device-management policies; ask your employer's IT team to approve execution on managed devices. Do not use this build to defeat endpoint protection.

GitHub Actions' public-repository hosted-runner usage is generally free under GitHub's current rules, subject to GitHub's terms, limits and future changes.
