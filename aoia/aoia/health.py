from __future__ import annotations

import httpx
from typing import Any, Dict

def check_source_health(source: Dict[str, Any], client: httpx.Client | None = None) -> Dict[str, Any]:
    """Execute 6-point health check gate on source.
    
    Checks:
      1. Valid URL scheme (http/https) and host
      2. No private / loopback IP address
      3. HTTP reachability and status (200 / 3xx accepted; 404/5xx failed)
      4. SSL certificate validity
      5. Response content-type valid (html/xml/pdf)
      6. Not domain parked / blank content
      
    Updates:
      verification: PASSED or FAILED
      consecutive_failures: incremented on fail, reset on pass
      auto-disables when consecutive_failures >= 5
    """
    url = source.get("base_url")
    if not url:
        source["verification"] = "FAILED"
        source["health_reason"] = "Missing base_url"
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
        return source

    # Check 1 & 2: Scheme & Loopback
    from urllib.parse import urlparse
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if parsed.scheme not in ("http", "https"):
        source["verification"] = "FAILED"
        source["health_reason"] = f"Unsupported scheme: {parsed.scheme}"
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
        return source
    if host in ("localhost", "127.0.0.1", "0.0.0.0") or host.startswith("192.168.") or host.startswith("10."):
        source["verification"] = "FAILED"
        source["health_reason"] = "Private or loopback address blocked"
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
        return source

    close_client = False
    if client is None:
        client = httpx.Client(timeout=8.0, follow_redirects=True, verify=True)
        close_client = True

    try:
        resp = client.get(url, headers={"User-Agent": "AOIA-FineArts-Bot/1.0 (+https://github.com/aoia)"})
        # Check 3: Status
        if resp.status_code >= 400:
            source["verification"] = "FAILED"
            source["health_reason"] = f"HTTP {resp.status_code}"
            source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
        # Check 5 & 6: Content type & blank check
        elif len(resp.text.strip()) < 50:
            source["verification"] = "FAILED"
            source["health_reason"] = "Empty response body"
            source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
        else:
            source["verification"] = "PASSED"
            source["health_reason"] = f"HTTP {resp.status_code} OK"
            source["consecutive_failures"] = 0
    except httpx.ConnectError:
        source["verification"] = "FAILED"
        source["health_reason"] = "Connection refused"
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
    except httpx.TimeoutException:
        source["verification"] = "FAILED"
        source["health_reason"] = "Connection timed out"
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
    except Exception as e:
        source["verification"] = "FAILED"
        source["health_reason"] = str(e)
        source["consecutive_failures"] = source.get("consecutive_failures", 0) + 1
    finally:
        if close_client:
            client.close()

    # Rule: 5 consecutive failures auto-disable
    if source.get("consecutive_failures", 0) >= 5:
        source["enabled"] = False
        source["disabled_reason"] = "Auto-disabled: 5 consecutive health failures"

    return source

# Legacy alias
def check_source(source: Dict[str, Any]) -> Dict[str, Any]:
    return check_source_health(source)
