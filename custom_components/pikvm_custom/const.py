"""Constants for the PiKVM Custom Controls integration."""

DOMAIN = "pikvm_custom"
PLATFORMS = ["button", "binary_sensor", "sensor", "camera", "switch", "select"]

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_USERNAME = "admin"
DEFAULT_VERIFY_SSL = False
