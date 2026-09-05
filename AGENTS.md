# AGENTS.md

# Project

MkDocs Material Documentation Portal.

The project provides public and password-protected documentation hosted entirely on GitHub Pages.

---

# Primary Objective

Build a maintainable technical documentation portal using:

```text
MkDocs
Material for MkDocs
Markdown
GitHub Actions
GitHub Pages
Vanilla JavaScript
Web Crypto API
```

Do not introduce unnecessary backend services.

---

# Core Architecture

```text
Markdown Documentation
        │
        ▼
MkDocs Material
        │
        ▼
Static Site Build
        │
        ▼
GitHub Actions
        │
        ▼
GitHub Pages
```

Secure pages:

```text
Request Page
    │
    ▼
secure-pages.js
    │
    ├── Public
    │      ↓
    │   Show Content
    │
    └── Secure
           ↓
       Lock Screen
           ↓
       Password
           ↓
       Web Crypto
           ↓
       Compare Hash
```

---

# Important Security Rule

GitHub Pages is static hosting.

The password protection implemented by this project is a client-side access gate.

Never describe it as equivalent to:

- server-side authentication;
- private hosting;
- zero-knowledge encryption;
- enterprise access control.

Never store actual production secrets in documentation.

Examples of forbidden content:

```text
private keys
API secrets
production passwords
database credentials
VPN private keys
customer credentials
authentication tokens
```

---

# Development Principles

Prioritize:

1. Simplicity.
2. Maintainability.
3. Minimal dependencies.
4. Markdown-first documentation.
5. Static hosting compatibility.
6. Fast page loading.
7. Easy deployment.
8. Clear security boundaries.

---

# Do Not Introduce

Unless explicitly requested:

```text
Node.js frontend framework
React
Vue
Angular
database
PHP backend
Python web server
Docker dependency for production
authentication server
external SaaS authentication
Cloudflare dependency
custom domain dependency
```

GitHub Pages must remain the production hosting target.

---

# Repository Structure

Maintain:

```text
docs/
config/
scripts/
.github/workflows/
mkdocs.yml
requirements.txt
PRD.md
AGENTS.md
TASKS.md
```

Do not place documentation Markdown outside `docs/`.

---

# Documentation Files

Use:

```text
docs/<category>/<document>.md
```

Example:

```text
docs/network/vyos.md
docs/network/bgp.md
docs/dns/unbound.md
```

Use lowercase filenames.

Use hyphens for multiple words.

Correct:

```text
wireguard-site-to-site.md
```

Avoid:

```text
WireGuard Site To Site.md
```

---

# Markdown Standard

Every documentation page should start with:

```markdown
# Page Title
```

Use hierarchical headings.

Example:

```markdown
# VyOS

## Overview

## Configuration

### BGP

### Static Routing

## Troubleshooting
```

---

# Command Examples

Use fenced code blocks.

Example:

```markdown
```bash
show interfaces
```
```

Use the correct language identifier wherever possible:

```text
bash
shell
yaml
json
python
javascript
php
sql
ini
```

---

# Secure Pages

Secure page configuration must be maintained separately from Markdown content.

Primary configuration:

```text
config/secure-pages.json
```

Do not require authors to embed authentication JavaScript inside documentation Markdown.

---

# Secure Page Configuration

Expected conceptual structure:

```json
{
  "secure_pages": [
    {
      "path": "/network/vyos/",
      "group": "vyos",
      "password_hash": "..."
    }
  ]
}
```

Keep configuration parsing centralized.

---

# Password Storage

Never store plaintext password in:

```text
JavaScript
HTML
Markdown
YAML
JSON
GitHub Actions
Git repository
```

Only password-derived hashes may be committed.

---

# Password Verification

Use browser-native:

```text
window.crypto.subtle
```

Preferred algorithm:

```text
SHA-256
```

If password derivation is improved later, prefer:

```text
PBKDF2
+
unique salt
+
high iteration count
```

Do not add third-party crypto libraries unless required.

---

# Session Handling

Use:

```text
sessionStorage
```

by default.

Unlock state should disappear after the relevant browser session/tab is closed.

Do not use cookies requiring backend validation.

Do not create fake JWT authentication.

---

# Password Groups

Support group-based unlocking.

Example:

```text
vyos-basic
network-internal
server-internal
```

If two secure pages belong to the same group, unlocking one may unlock the other for the current session.

---

# UI

Secure lock screen must integrate visually with Material for MkDocs.

Requirements:

```text
responsive
light mode
dark mode
keyboard accessible
Enter submits form
clear wrong-password error
```

Do not use browser-native:

```javascript
prompt()
```

unless only as a temporary development implementation.

Production should use an inline lock form.

---

# Secure Content Handling

Before authentication, protected page content must not be visible in the normal rendered UI.

Do not solve protection merely by:

```css
display: none
```

without an authentication layer controlling rendering.

However, remember that the generated static files are still retrievable and therefore this mechanism does not provide server-side confidentiality.

---

# Search

Be careful with MkDocs search indexing.

Secure page body content should not be exposed through search suggestions if avoidable.

If native MkDocs search cannot exclude protected content cleanly, implement one of:

1. Exclude secure pages from search indexing.
2. Remove secure-page body text from generated search index.
3. Only expose secure page title.

Do not allow protected documentation body text to appear in search results before unlock.

---

# Navigation

Protected pages should contain a visible lock marker.

Example:

```yaml
- VyOS 🔒: network/vyos.md
```

Keep this solution simple for V1.

---

# Validation

Create validation utilities under:

```text
scripts/
```

Validation should detect:

- malformed JSON;
- duplicate path;
- duplicate conflicting configuration;
- missing secure document;
- invalid group;
- empty hash.

GitHub Actions should fail before deployment when validation fails.

---

# Local Development

The canonical local command is:

```bash
mkdocs serve
```

Do not require Docker.

---

# Python

Utility scripts must:

- support Python 3.11+;
- have readable functions;
- produce useful errors;
- avoid unnecessary external dependencies.

Use standard library where possible.

---

# JavaScript

Use vanilla JavaScript.

Requirements:

- no jQuery;
- no React;
- no Vue;
- no bundler unless absolutely necessary;
- modern browser APIs;
- small modules;
- avoid global variables where possible.

---

# CSS

Custom styles should live under:

```text
docs/assets/stylesheets/
```

Do not modify Material theme package files directly.

---

# MkDocs Theme Overrides

If theme overrides are necessary use:

```text
docs/overrides/
```

Do not edit installed package source.

---

# GitHub Actions

Production deployment must happen from GitHub Actions.

Workflow must perform:

```text
checkout
setup Python
install dependencies
validate secure configuration
build MkDocs
deploy GitHub Pages
```

Deployment target:

```text
GitHub Pages
```

No custom domain should be required.

---

# Base URL

The application must support repository-based GitHub Pages URLs.

Example:

```text
https://username.github.io/documentation/
```

Never assume site is hosted at:

```text
/
```

All custom JavaScript and paths must work when the site has a repository prefix.

---

# Path Handling

This is extremely important.

Do not hardcode:

```text
/network/vyos/
```

in a way that breaks:

```text
https://username.github.io/documentation/network/vyos/
```

Secure-page matching must account for the GitHub Pages repository prefix.

---

# Git Rules

Keep commits focused.

Suggested prefixes:

```text
feat:
fix:
docs:
refactor:
chore:
security:
```

Examples:

```text
feat: add secure page authentication
docs: add VyOS documentation
fix: handle GitHub Pages base path
```

---

# Testing

At minimum test:

```text
public page
secure page
correct password
incorrect password
empty password
page reload
session unlock
direct URL access
mobile layout
dark mode
GitHub Pages subpath
multiple secure pages
password groups
search leakage
```

---

# Acceptance Priority

Prioritize functionality in this order:

```text
MkDocs works
    ↓
Material theme works
    ↓
GitHub Pages works
    ↓
Public documentation works
    ↓
Secure page identification works
    ↓
Lock UI works
    ↓
Password verification works
    ↓
Session works
    ↓
Search leakage protection
    ↓
Polish
```

---

# When Modifying Existing Code

Before changing code:

1. Read `PRD.md`.
2. Read `AGENTS.md`.
3. Read `TASKS.md`.
4. Inspect current repository structure.
5. Preserve existing working functionality.
6. Make the smallest reasonable change.
7. Test locally when possible.
8. Update `TASKS.md` when task status changes.

---

# Definition of Correct Implementation

A correct implementation allows:

```text
Network
├── MikroTik
├── VyOS 🔒
├── BGP
└── WireGuard
```

where:

```text
MikroTik
BGP
WireGuard
```

open normally, while:

```text
VyOS
```

shows a password screen before the documentation UI is exposed.

The site must remain deployable at:

```text
https://<username>.github.io/<repository>/
```

without a custom domain.