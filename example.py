import os

import proxyx

app = proxyx.ProxyApp(
    hostname=os.environ["PROXYX_HOSTNAME"],
    root_path=os.environ.get("PROXYX_ROOT_PATH", ""),
)
