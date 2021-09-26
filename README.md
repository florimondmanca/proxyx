# ProxyX

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.proxyx?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=14&branchName=master)

Proof of concept for a lightweight HTTP/1.1 proxy service built with [ASGI](https://asgi.readthedocs.io) and [HTTPX](https://github.com/encode/httpx). No maintenance intended.

## Setup

Clone this repository, then install dependencies:

```bash
scripts/install
```

## Example

```bash
scripts/example
```

This will proxy https://www.python-httpx.org/ (the HTTPX documentation) from `localhost:8000`.

Use environment variables as below to proxy a different target:

```bash
PROXYX_HOSTNAME="www.example.org" PROXYX_ROOT_PATH="" scripts/example
```

## Known limitations

- Domain-level redirects are not handled (e.g. proxying `https://encode.io/{path}` won't work because this domain returns a 301 to `https://www.encode.io/{path}`).

## License

MIT
