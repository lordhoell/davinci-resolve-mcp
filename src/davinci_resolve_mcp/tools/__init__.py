"""Tool modules for DaVinci Resolve MCP Server.

Each module corresponds to one Resolve API object (Resolve, ProjectManager, etc.)
and registers its tools via the @mcp.tool() decorator.

Importing this package imports all tool modules.
"""

from davinci_resolve_mcp.tools import resolve  # noqa: F401

from davinci_resolve_mcp.tools import project_manager  # noqa: F401
from davinci_resolve_mcp.tools import project  # noqa: F401

from davinci_resolve_mcp.tools import media_storage  # noqa: F401
from davinci_resolve_mcp.tools import media_pool  # noqa: F401
from davinci_resolve_mcp.tools import folder  # noqa: F401
from davinci_resolve_mcp.tools import media_pool_item  # noqa: F401

from davinci_resolve_mcp.tools import timeline  # noqa: F401
from davinci_resolve_mcp.tools import timeline_item  # noqa: F401

from davinci_resolve_mcp.tools import gallery  # noqa: F401
from davinci_resolve_mcp.tools import graph  # noqa: F401
from davinci_resolve_mcp.tools import color_group  # noqa: F401

from davinci_resolve_mcp.tools import utility  # noqa: F401

from davinci_resolve_mcp.tools import fusion_comp    # noqa: F401
from davinci_resolve_mcp.tools import fusion_tool    # noqa: F401
from davinci_resolve_mcp.tools import fusion_input   # noqa: F401
from davinci_resolve_mcp.tools import fusion_output  # noqa: F401
from davinci_resolve_mcp.tools import fusion_flow    # noqa: F401
from davinci_resolve_mcp.tools import fusion_spline  # noqa: F401
from davinci_resolve_mcp.tools import fusion_misc    # noqa: F401
