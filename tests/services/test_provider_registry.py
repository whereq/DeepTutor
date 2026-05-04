from deeptutor.services.provider_registry import find_by_name, find_gateway


def test_nvidia_nim_gateway_detection_by_key_and_base() -> None:
    spec = find_by_name("nvidia_nim")

    assert spec is not None
    assert spec.supports_stream_options is False
    assert find_gateway(api_key="nvapi-test-key") == spec
    assert find_gateway(api_base="https://integrate.api.nvidia.com/v1") == spec
