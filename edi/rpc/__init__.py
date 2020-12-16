from .rpc import OdooGetCogsRpc, OdooGetStockRpc, OdooListStockRpc


get_cogs_rpc = OdooGetCogsRpc()
get_cogs_rpc.daemon = True
get_cogs_rpc.start()

get_stock_rpc = OdooGetStockRpc()
get_stock_rpc.daemon = True
get_stock_rpc.start()

list_stock_rpc = OdooListStockRpc()
list_stock_rpc.daemon = True
list_stock_rpc.start()
