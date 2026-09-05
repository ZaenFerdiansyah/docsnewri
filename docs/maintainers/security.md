# Security Boundaries

## Static-hosting limitation

GitHub Pages is static hosting. The secure-page feature in this portal is a client-side access gate implemented in the visitor's browser.

It can keep protected content out of the normal rendered interface and public search results until a password is accepted. It is not equivalent to server-side authentication, private hosting, enterprise access control, or encrypted document storage.

A person capable of inspecting or retrieving generated static assets may still access their contents. Documentation requiring real confidentiality must use a platform with server-side authentication and authorization.

## Prohibited secrets

Never store highly sensitive or production secrets in this portal, whether a page is public or protected. Prohibited examples include:

- private keys;
- production passwords;
- API secrets;
- database credentials;
- VPN private keys;
- authentication tokens;
- customer credentials.

Do not place these values in Markdown, HTML, JavaScript, YAML, JSON, GitHub Actions, examples, or repository history.

Only password-derived hashes may be committed for the client-side access gate. A committed hash does not make the generated static content confidential.

## Search behavior

The build derives protected paths from `config/secure-pages.json`. It keeps only each protected page's top-level title and URL in the public search index and removes protected headings, commands, and body text.

Search filtering reduces accidental exposure through search suggestions. It does not encrypt the protected page HTML.
