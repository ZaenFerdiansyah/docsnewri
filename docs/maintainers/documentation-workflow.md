# Documentation Maintainer Workflow

## Add a documentation page

Create Markdown inside the appropriate category under `docs/`. Use a lowercase filename and hyphens between words.

For example:

```text
docs/network/ospf.md
```

Every page starts with one level-one heading and uses hierarchical headings below it:

```markdown
# OSPF

## Overview

OSPF documentation.
```

Use fenced code blocks with an appropriate language identifier for commands and configuration.

## Add the page to navigation

Add the source path to `nav` in `mkdocs.yml`:

```yaml
nav:
  - Network:
      - OSPF: network/ospf.md
```

Use a visible lock marker when the page is protected:

```yaml
- OSPF 🔒: network/ospf.md
```

Run a strict build after changing navigation. A missing or incorrect Markdown path must be fixed before committing.

## Make a page secure

Secure status is configured separately from Markdown. Do not add authentication JavaScript to a documentation page.

First generate a password hash:

```bash
python scripts/generate-password-hash.py
```

The utility requests the password twice without echoing it. Copy only the resulting hash into `config/secure-pages.json`:

```json
{
  "path": "/network/ospf/",
  "group": "network-internal",
  "password_hash": "64-character-sha256-hash"
}
```

Paths are site-relative documentation routes. They must start and end with `/`; do not include the GitHub Pages repository prefix.

Add `🔒` to the corresponding navigation label, then validate and test the page.

## Password groups

The `group` value controls session sharing. Pages with the same group must have the same password hash. Unlocking one of those pages unlocks the other pages in that group for the current browser tab/session.

Pages that must remain independent use different group values. The validator rejects a shared group containing different password hashes.

## Change a password

Run the hash generator again and replace `password_hash` for every page in the affected group. Never commit the plaintext password.

Changing the hash invalidates previously stored session unlock state because session state is tied to the configured hash.

Validate, build, and test both the old and new passwords before deployment. The old password must fail and the new password must succeed.

## Remove protection

Remove the page entry from `config/secure-pages.json`, then remove the lock marker from `mkdocs.yml`.

After rebuilding, confirm that:

- the page opens without a password;
- its public body is searchable;
- other pages in the former group remain protected when still configured.

## Test locally

Install dependencies and validate the secure configuration:

```bash
python -m pip install -r requirements.txt
python scripts/validate-secure-pages.py
```

Start the development server:

```bash
mkdocs serve
```

At minimum, test public and secure direct URLs, empty/wrong/correct passwords, reload behavior, a fresh browser session, shared and independent groups, mobile layout, light/dark modes, Enter-key submission, and protected search terms.

Run the automated tests and strict production build:

```bash
python -m unittest discover -s tests -v
mkdocs build --strict
```

Inspect `site/search/search_index.json` when secure content or the search implementation changes. A protected page may retain its top-level title, but its headings, commands, and body must not be present.

## Deployment

A push to `main` starts `.github/workflows/deploy.yml`. The workflow:

1. checks out the repository;
2. installs Python dependencies;
3. validates `config/secure-pages.json` and its document paths;
4. runs `mkdocs build --strict`;
5. uploads the generated `site/` directory as a GitHub Pages artifact;
6. deploys that artifact to GitHub Pages.

Validation or build failure stops deployment. Generated `site/` output is ignored locally and is not committed.
