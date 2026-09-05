# Zensnewri Documentation

Static technical documentation built with MkDocs Material and published through GitHub Pages.

## Local development

Install the dependencies and start the local development server:

```bash
python -m pip install -r requirements.txt
mkdocs serve
```

Create a production build with strict validation:

```bash
mkdocs build --strict
```

All documentation source files live under `docs/`.

## Security boundary

GitHub Pages is static hosting. The client-side page gate must not be treated as server-side authentication or a confidentiality control. Never store production passwords, private keys, API secrets, access tokens, or customer credentials in this repository.

Maintainer procedures and the complete security boundary are documented in `docs/maintainers/`.

### Protected pages in search

The build hook derives protected paths from `config/secure-pages.json`. In the public MkDocs search index, it keeps the protected page's top-level title and URL but removes its body, headings, commands, and other section entries. Public page content remains fully searchable.

This search filtering reduces accidental disclosure through the search interface. It does not encrypt generated HTML or turn the client-side access gate into server-side security.

### GitHub Pages paths

Documentation links and custom assets use relative URLs. The secure-page script derives both the site base path and configuration URL from its own loaded URL, so deployment under `https://<username>.github.io/<repository>/` does not assume a domain root. The build hook also converts root-relative links emitted by MkDocs for `404.html` into repository-safe relative links.
