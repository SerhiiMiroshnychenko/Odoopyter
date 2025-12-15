import sys
import logging
from dataclasses import dataclass
from typing import Any, Optional, Type

# Constants
ODOO_PATH = r'D:\ODOOs\COMMUNITY\odoo19'
DB_NAME = 'odoo_db'
ODOO_CONFIG_PATH = r'D:\CUSTOMs\MY\Odoopyter\odoo.conf'

logger = logging.getLogger(__name__)


@dataclass
class OdooContext:
    registry: Any
    cr: Any
    env: Any
    env_user: Any

    def close(self) -> None:
        if self.cr is not None:
            self.cr.close()
            self.cr = None

    def __enter__(self) -> "OdooContext":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> bool:
        if exc_type is not None and self.cr is not None:
            self.cr.rollback()
        self.close()
        return False


def init_odoo_context() -> OdooContext:
    if ODOO_PATH not in sys.path:
        sys.path.insert(0, ODOO_PATH)

    import odoo
    from odoo import api, SUPERUSER_ID

    odoo.tools.config.parse_config([
        '-c', ODOO_CONFIG_PATH,
        '-d', DB_NAME
    ])

    registry = odoo.modules.registry.Registry.new(DB_NAME)
    cr = registry.cursor()
    env = api.Environment(cr, SUPERUSER_ID, {})
    env_user = env.user
    return OdooContext(registry=registry, cr=cr, env=env, env_user=env_user)


def main() -> OdooContext:
    ctx = init_odoo_context()

    logger.info("Odoo environment is ready.")
    logger.info("  Database: %s", DB_NAME)

    return ctx


if __name__ == "__main__":
    ctx = main()
    registry = ctx.registry
    cr = ctx.cr
    env = ctx.env
    env_user = ctx.env_user
