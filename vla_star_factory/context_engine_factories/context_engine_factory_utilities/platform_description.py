import platform
import os

def get_platform_description():
    """Return a short description suitable for filling in a sentence."""
    info_parts = []

    # Basic OS info
    info_parts.append(platform.system())               # e.g., 'Linux'
    info_parts.append(platform.release())              # kernel version
    info_parts.append(platform.machine())              # 'x86_64', etc.

    # Python info
    
    # Optional: distro info
    try:
        import distro
        info_parts.append(f"{distro.name()} {distro.version()}")
    except ImportError:
        # fallback: /etc/os-release
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        info_parts.append(line.strip().split("=")[1].strip('"'))
                        break
        except Exception:
            pass
    
    
    info_parts.append(f"User: {os.environ["USER"]}")
    info_parts.append(f"Python {platform.python_version()}")
    # Return only the part to fill the braces
    return ', '.join(info_parts)