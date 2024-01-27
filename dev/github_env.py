"""Helper to determine to correct Python and OS version."""

import os
import platform


def get_os():
    if platform.system() == "Linux":
        try:
            import subprocess

            return subprocess.run(
                ["/usr/bin/lsb_release", "--description", "--short"],
                capture_output=True,
                shell=False,
                text=True,
            ).stdout.splitlines()[0]
        except Exception:
            pass

    if platform.system() == "Windows":
        versions = {
            14393: "Windows Server 2016 (1607)",
            16299: "Windows Server 2016 (1709)",
            17134: "Windows Server 2016 (1803)",
            17763: "Windows Server 2019 (1809)",
            18362: "Windows Server 2019 (1903)",
            18363: "Windows Server 2019 (1909)",
            19041: "Windows Server 2019 (2004)",
            19042: "Windows Server 2019 (20H2)",
            20348: "Windows Server 2022 (21H2)",
        }
        try:
            build = int(platform.version().split(".")[-1])
            return versions[build]
        except Exception:
            pass
    if platform.system() == "Darwin":
        return f"{platform.release()!r} {platform.version()!r}"

    return platform.platform()


with open(os.environ["GITHUB_ENV"], "a") as f:
    f.write(f"PYTHON={platform.python_version()}\n")
    f.write(f"OS={get_os()}\n")
