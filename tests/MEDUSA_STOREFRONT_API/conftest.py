import os
import re
import json
import yaml
import pytest
import requests
import pathlib

from requests.adapters import HTTPAdapter

# Prefer vendored urllib3 Retry inside requests to avoid extra imports; fallback if unavailable
try:
    Retry = requests.packages.urllib3.util.retry.Retry  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    from urllib3.util.retry import Retry  # type: ignore


_ENV_PATTERN = re.compile(r"\$\{([^}:\s]+):-([^}]+)}")


def _expand_env_vars(value):
    if isinstance(value, str):
        def _replace(match):
            var_name = match.group(1)
            default_val = match.group(2)
            env_val = os.environ.get(var_name)
            if env_val is None or env_val == "":
                return default_val
            return env_val
        return _ENV_PATTERN.sub(_replace, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    else:
        return value


def _load_config_dict():
    cfg_path = pathlib.Path(__file__).parent.joinpath("config.yml")
    if not cfg_path.exists():
        pytest.fail(f"Missing required config.yml at: {cfg_path}")
    try:
        raw = cfg_path.read_text(encoding="utf-8")
    except Exception as e:
        pytest.fail(f"Failed to read config.yml at {cfg_path}: {e}")
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in config.yml at {cfg_path}: {e}")
    data = _expand_env_vars(data)
    return data


@pytest.fixture(scope="session")
def config():
    return _load_config_dict()


@pytest.fixture
def get_config(config):
    def _getter(dotted_key, default=None):
        if not dotted_key:
            return default
        current = config
        for part in dotted_key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    return _getter


@pytest.fixture
def load_endpoint_test_data(request):
    def _loader(path):
        if not path:
            raise ValueError("A JSON path must be provided to load_endpoint_test_data(path)")
        p = pathlib.Path(path)
        if not p.is_absolute():
            candidates = [
                pathlib.Path.cwd() / p,
                pathlib.Path(getattr(request, "fspath", "." )).parent / p,
                pathlib.Path(getattr(request.config, "rootpath", ".")) / p,
            ]
            for c in candidates:
                if c.exists():
                    p = c
                    break
        if not p.exists():
            raise FileNotFoundError(f"Endpoint test data file not found: {path}")
        try:
            with p.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {p}: {e}") from e
    return _loader


@pytest.fixture
def merged_test_data(config, load_endpoint_test_data):
    def _merger(path=None):
        base = {}
        cfg_td = config.get("test_data")
        if isinstance(cfg_td, dict):
            base = dict(cfg_td)  # shallow copy
        if path:
            endpoint_data = load_endpoint_test_data(path)
            if not isinstance(endpoint_data, dict):
                raise TypeError("Endpoint test data must be a JSON object (top-level dictionary)")
            # endpoint overrides on conflict
            base.update(endpoint_data)
        return base
    return _merger


class APIClient:
    def __init__(
        self,
        base_url,
        default_headers=None,
        timeout=30,
        retries=3,
        backoff=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        session=None,
    ):
        if not base_url or not isinstance(base_url, str):
            raise ValueError("base_url must be a non-empty string")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if Retry is None:
            raise RuntimeError("Retry class is not available; ensure urllib3 is installed")
        retry_cfg = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_cfg)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.default_headers = dict(default_headers or {})

    def _compose_url(self, endpoint):
        if not isinstance(endpoint, str):
            raise ValueError("endpoint must be a string")
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self.base_url}{'' if endpoint.startswith('/') else '/'}{endpoint}"

    def make_request(self, endpoint, method="GET", headers=None, timeout=None, **kwargs):
        url = self._compose_url(endpoint)
        req_headers = {}
        req_headers.update(self.default_headers)
        if headers:
            req_headers.update(headers)
        t = timeout if timeout is not None else self.timeout
        return self.session.request(method=method.upper(), url=url, headers=req_headers, timeout=t, **kwargs)

    def get(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="GET", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="POST", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PUT", **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="PATCH", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.make_request(endpoint, method="DELETE", **kwargs)


@pytest.fixture
def api_client(config):
    api_cfg = config.get("api") or {}
    host = api_cfg.get("host")
    if not isinstance(host, str) or not host.strip():
        pytest.fail("`api.host` is missing or empty in config.yml")
    base_url = host.strip()

    timeout = api_cfg.get("timeout", 30)
    retries = api_cfg.get("retries", 3)
    backoff = api_cfg.get("backoff", 0.3)
    status_forcelist = tuple(api_cfg.get("status_forcelist", [429, 500, 502, 503, 504]))

    default_headers = {}
    dh = api_cfg.get("default_headers")
    if isinstance(dh, dict):
        default_headers = {str(k): str(v) for k, v in dh.items()}

    return APIClient(
        base_url=base_url,
        default_headers=default_headers,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
        status_forcelist=status_forcelist,
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark a test as a smoke test")
