# ProxyCore

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.proxycore?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=14&branchName=master)

Proof of concept for a lightweight HTTP/1.1 proxy service built with [ASGI](https://asgi.readthedocs.io) and [HTTPCore](https://github.com/encode/httpcore). No maintenance intended.

## Setup

Clone this repository, then install dependencies:

```bash
scripts/install
```

## Example

```bash
scripts/example
```

This will proxy https://www.encode.io/httpcore (the HTTPCore documentation) from `localhost:8000`.

## Known limitations

- Domain-level redirects are not handled (e.g. proxying `https://encode.io/{path}` won't work because this domain returns a 301 to `https://www.encode.io/{path}`).

## License

MIT
