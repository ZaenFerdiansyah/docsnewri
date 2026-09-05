# TASKS.md

# MkDocs Documentation Portal

Status legend:

```text
[ ] Pending
[-] In Progress
[x] Completed
```

---

# PHASE 01 — Project Foundation

## TASK 01 — Initialize Project

[x] Create project repository structure.

Required:

```text
docs/
config/
scripts/
.github/workflows/
```

Create:

```text
mkdocs.yml
requirements.txt
README.md
PRD.md
AGENTS.md
TASKS.md
```

Acceptance:

```text
repository has clean initial structure
```

---

## TASK 02 — Install MkDocs

[x] Add MkDocs dependencies.

Minimum:

```text
mkdocs
mkdocs-material
```

Create `requirements.txt`.

Acceptance:

```bash
pip install -r requirements.txt
```

completes successfully.

---

## TASK 03 — Create Basic MkDocs Configuration

[x] Configure:

```text
site_name
theme
navigation
plugins
markdown extensions
extra CSS
extra JavaScript
```

Theme:

```yaml
theme:
  name: material
```

Acceptance:

```bash
mkdocs serve
```

starts successfully.

---

# PHASE 02 — Documentation UI

## TASK 04 — Create Homepage

[x] Create:

```text
docs/index.md
```

Include:

```text
portal title
description
main categories
search instructions
```

---

## TASK 05 — Create Initial Categories

[x] Create:

```text
docs/network/
docs/dns/
docs/server/
docs/monitoring/
```

---

## TASK 06 — Create Initial Network Pages

[x] Create:

```text
docs/network/index.md
docs/network/mikrotik.md
docs/network/vyos.md
docs/network/bgp.md
docs/network/wireguard.md
```

---

## TASK 07 — Configure Navigation

[x] Implement:

```text
Network
├── MikroTik
├── VyOS 🔒
├── BGP
└── WireGuard
```

Acceptance:

All pages appear in sidebar navigation.

---

# PHASE 03 — Material Features

## TASK 08 — Enable Navigation Features

[x] Enable relevant Material features:

```text
navigation.tabs
navigation.sections
navigation.expand
navigation.top
toc.follow
```

---

## TASK 09 — Enable Code Features

[x] Enable:

```text
syntax highlighting
copy button
code annotations
content tabs
```

---

## TASK 10 — Enable Dark Mode

[x] Add light/dark color palette toggle.

Acceptance:

User can switch light/dark mode.

---

## TASK 11 — Configure Search

[x] Enable MkDocs search.

Acceptance:

Public documentation is searchable.

---

# PHASE 04 — Secure Page Core

## TASK 12 — Create Secure Page Configuration

[x] Create:

```text
config/secure-pages.json
```

Initial secure page:

```text
VyOS
```

Conceptual configuration:

```json
{
  "secure_pages": [
    {
      "path": "/network/vyos/",
      "group": "vyos",
      "password_hash": ""
    }
  ]
}
```

---

## TASK 13 — Create Secure Configuration Loader

[x] Implement client-side loading of secure page configuration.

Requirements:

- Works on GitHub Pages.
- Works with repository subpath.
- Does not assume root `/`.
- Handles malformed or missing configuration gracefully.

---

## TASK 14 — Detect Secure Page

[x] Create logic to determine:

```text
current page = public
```

or:

```text
current page = secure
```

Acceptance:

Only configured pages invoke lock functionality.

---

# PHASE 05 — Password System

## TASK 15 — Create Password Hash Generator

[x] Create:

```text
scripts/generate-password-hash.py
```

Input:

```text
password
confirm password
```

Output:

```text
password hash
```

Requirements:

- Never save plaintext password.
- Never echo password unnecessarily.
- Clear error when confirmation differs.

---

## TASK 16 — Implement Browser Password Hashing

[x] Create:

```text
docs/assets/javascripts/secure-pages.js
```

Use:

```text
Web Crypto API
```

Initial hash:

```text
SHA-256
```

Do not use third-party crypto library.

---

## TASK 17 — Compare Password Hash

[x] Compare user password-derived hash against configured hash.

Acceptance:

```text
correct password → true
wrong password   → false
```

---

# PHASE 06 — Lock Screen

## TASK 18 — Create Lock UI

[x] Build inline password interface.

Include:

```text
lock icon
Protected Documentation title
password field
Unlock button
error area
```

Do not use:

```javascript
prompt()
```

in final implementation.

---

## TASK 19 — Create Secure Page CSS

[x] Create:

```text
docs/assets/stylesheets/secure.css
```

Requirements:

- Material-compatible.
- Responsive.
- Light mode.
- Dark mode.
- Centered lock panel.
- Accessible input/button.

---

## TASK 20 — Hide Documentation UI Until Unlock

[x] Secure page should initially show lock screen.

After valid password:

```text
hide lock screen
show documentation
```

Acceptance:

Normal visitor does not see secure page body in the rendered UI before unlock.

---

## TASK 21 — Wrong Password Handling

[x] Display:

```text
Incorrect password.
```

Requirements:

- Do not reload page.
- Preserve password focus.
- Clear input where appropriate.
- Enter key supported.

---

# PHASE 07 — Session

## TASK 22 — Implement Session Unlock

[x] Store valid unlock in:

```text
sessionStorage
```

---

## TASK 23 — Reload Behavior

[x] If current secure group has valid session:

```text
reload page
    ↓
skip password screen
```

---

## TASK 24 — Session Expiration

[x] Default behavior:

```text
close browser tab/session
    ↓
unlock removed
```

No permanent authentication required for V1.

---

# PHASE 08 — Password Groups

## TASK 25 — Add Group Support

[x] Support:

```text
group
```

Example:

```json
{
  "path": "/network/vyos/",
  "group": "network-internal"
}
```

---

## TASK 26 — Group Session Unlock

[x] When multiple pages use:

```text
network-internal
```

unlocking one page should unlock all pages in that group for the current session.

---

# PHASE 09 — Secure Page Validation

## TASK 27 — Create Configuration Validator

[x] Create:

```text
scripts/validate-secure-pages.py
```

Validate:

```text
JSON syntax
required fields
duplicate paths
empty hashes
invalid groups
```

---

## TASK 28 — Validate Documentation Path

[x] Validator should confirm configured secure page corresponds to an actual built documentation page.

Build should fail for invalid entries.

---

# PHASE 10 — Search Security

## TASK 29 — Inspect MkDocs Search Index

[x] Determine whether secure page content appears in:

```text
search/search_index.json
```

---

## TASK 30 — Prevent Secure Body Search Leakage

[x] Implement protection so secure documentation body is not exposed through normal search results.

Preferred outcome:

```text
secure title visible
secure content hidden
```

Alternative:

```text
secure page completely excluded from search
```

Acceptance:

Searching words that exist only inside VyOS protected body does not reveal the protected text.

---

# PHASE 11 — Direct URL Handling

## TASK 31 — Test Direct Secure URL

[x] Opening directly:

```text
https://username.github.io/documentation/network/vyos/
```

must show lock UI.

---

## TASK 32 — Test Public Direct URL

[x] Opening:

```text
https://username.github.io/documentation/network/bgp/
```

must immediately show documentation.

---

# PHASE 12 — GitHub Pages Compatibility

## TASK 33 — Handle Repository Base Path

[x] Ensure JavaScript correctly supports:

```text
https://username.github.io/documentation/
```

Do not assume:

```text
https://username.github.io/
```

---

## TASK 34 — Verify Asset URLs

[x] Test:

```text
CSS
JavaScript
images
secure page config
navigation links
search assets
```

under GitHub Pages repository prefix.

---

# PHASE 13 — GitHub Actions

## TASK 35 — Create GitHub Actions Workflow

[x] Create:

```text
.github/workflows/deploy.yml
```

Workflow:

```text
Checkout
    ↓
Setup Python
    ↓
Install dependencies
    ↓
Validate secure pages
    ↓
Build MkDocs
    ↓
Deploy GitHub Pages
```

---

## TASK 36 — Configure GitHub Pages Deployment

[x] Use GitHub's supported Pages deployment workflow.

Deployment trigger:

```text
push → main
```

---

## TASK 37 — Fail Deployment on Validation Error

[x] Deployment must stop when:

```text
secure config invalid
mkdocs build fails
documentation reference invalid
```

---

# PHASE 14 — Testing

## TASK 38 — Public Page Test

[x] Test MikroTik.

Expected:

```text
No password required.
```

---

## TASK 39 — Secure Page Test

[x] Test VyOS.

Expected:

```text
Password required.
```

---

## TASK 40 — Incorrect Password Test

[x] Verify wrong password cannot unlock page UI.

---

## TASK 41 — Correct Password Test

[x] Verify correct password unlocks page.

---

## TASK 42 — Session Test

[x] Verify page remains unlocked during expected session.

---

## TASK 43 — New Session Test

[x] Close session and reopen.

Expected:

```text
Password required again.
```

---

## TASK 44 — Multiple Secure Pages Test

[x] Configure second secure page.

Verify independent and grouped modes.

---

## TASK 45 — Mobile Test

[x] Test lock UI on mobile-sized viewport.

---

## TASK 46 — Dark Mode Test

[x] Verify lock UI in dark mode.

---

## TASK 47 — Search Leakage Test

[x] Verify protected documentation body does not appear in public search suggestions/results.

---

# PHASE 15 — Documentation Author Workflow

## TASK 48 — Document "Add New Page"

[x] Add instructions for:

```text
create Markdown
add nav item
test
commit
push
```

---

## TASK 49 — Document "Protect Page"

[x] Add instructions explaining:

```text
generate password hash
add secure config
deploy
test
```

---

## TASK 50 — Document "Change Password"

[x] Process:

```text
generate new hash
replace existing hash
commit
deploy
```

---

## TASK 51 — Document "Remove Protection"

[x] Removing page from secure configuration should make it public after deployment.

---

# PHASE 16 — Security Documentation

## TASK 52 — Add Security Warning

[x] Clearly document:

```text
GitHub Pages = static hosting.
```

Secure pages provide an access gate, not server-side confidentiality.

---

## TASK 53 — Add Forbidden Secret Guidelines

[x] Explicitly prohibit storing:

```text
private keys
passwords
API secrets
customer credentials
VPN private keys
access tokens
```

---

# PHASE 17 — Final Polish

## TASK 54 — Add Lock Indicator

[x] Navigation:

```text
VyOS 🔒
```

---

## TASK 55 — Improve 404 Page

[x] Create custom documentation-friendly 404 page.

---

## TASK 56 — Improve Homepage

[x] Add category cards or clean navigation blocks.

---

## TASK 57 — Add Edit-on-GitHub Link

[ ] Optional.

Allow authorized documentation maintainers to quickly edit Markdown in GitHub.

Pending: no valid Git repository metadata, remote URL, or `repo_url` is available
in the current workspace. A placeholder would create broken edit links.

---

# PHASE 18 — Release

## TASK 58 — Production Build

[x] Run:

```bash
mkdocs build --strict
```

No errors.

---

## TASK 59 — Deploy Production

[ ] Push to:

```text
main
```

GitHub Actions completes successfully.

Pending: the workspace is not a valid Git repository and has no GitHub remote or
deployment credentials, so it cannot be pushed to `main` from this environment.

---

## TASK 60 — Verify GitHub Pages

[ ] Verify production URL:

```text
https://<username>.github.io/<repository>/
```

Pending: no deployed GitHub Pages URL or completed remote workflow run is
available to verify from this environment.

---

# FINAL ACCEPTANCE

Project is complete when this works:

```text
GitHub Pages
│
└── Documentation
    │
    ├── Network
    │   ├── MikroTik        PUBLIC
    │   ├── VyOS 🔒        PASSWORD
    │   ├── BGP             PUBLIC
    │   └── WireGuard       PUBLIC
    │
    ├── DNS                 PUBLIC
    │
    ├── Server
    │   └── ESXi 🔒         PASSWORD
    │
    └── Monitoring          PUBLIC
```

And the content workflow remains:

```text
Edit Markdown
    ↓
Commit
    ↓
Push
    ↓
GitHub Actions
    ↓
GitHub Pages updated
```
