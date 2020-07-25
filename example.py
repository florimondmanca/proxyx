import os

import proxycore

app = proxycore.ProxyApp(
    hostname=os.environ["PROXYCORE_HOSTNAME"],
    root_path=os.environ.get("PROXYCORE_ROOT_PATH", ""),
)
