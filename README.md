# ProxyCore

Proof of concept for a lightweight HTTP/1.1 proxy service built with [ASGI](https://asgi.readthedocs.io) and [HTTPCore](https://github.com/encode/httpcore). No maintenance intended.

## Example (Docker)

Clone this repo, then:

```bash
docker build -t proxycore .
docker run --rm -it -e PROXYCORE_HOSTNAME=encode.io -e PROXYCORE_ROOT_PATH=/httpcore -p 8000:8000 proxycore
```

This will proxy https://www.encode.io/httpcore (the HTTPCore documentation) from `localhost:8000`.

## Example (Host)

Clone this repo, then:

```bash
pip install -r requirements.txt
PROXYCORE_HOSTNAME=encode.io PROXYCORE_ROOT_PATH=/httpcore uvicorn proxycore:app
```

This will proxy https://www.encode.io/httpcore (the HTTPCore documentation) from `localhost:8000`.

## License

MIT
