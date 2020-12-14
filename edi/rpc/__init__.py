from .rpc import OdooGetCogsRpc


get_cogs_rpc = OdooGetCogsRpc()
get_cogs_rpc.daemon = True
get_cogs_rpc.start()
