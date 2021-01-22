
import json
import time
import xmlrpc.client


class OdooResolver:
    def __init__(self, data=None):
        try:
            url = 'https://smsperkasa.odoo.com/'
            self.db = 'smsperkasa-master-1574977'
            self.username = 'admin'
            self.password = '30ac227dc37f5b061a57cc984499ccd732e5d6a5'

            # If we want to authenticate the user first.
            # But it will takes more time.
            # common = xmlrpc.client.ServerProxy(
            #     '{}xmlrpc/2/common'.format(url))
            # self.uid = common.authenticate(
            #     self.db, self.username, self.password, {})

            # Bypass authentication, Assume we know the uid of the user.
            self.uid = 2

            self.models = xmlrpc.client.ServerProxy(
                '{}xmlrpc/2/object'.format(url))
            self.data = data
        except Exception as e:
            return str(e)

    def get_cogs(self):
        try:
            start = time.perf_counter()
            if self.data:
                data = self.data
                print(data)
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[['id', 'in', data]]],
                    {'fields': ['name', 'standard_price']}
                )
            else:
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[]], {'fields': ['name', 'standard_price']}
                )
            result = json.dumps(result)
            print('Get COGS xmlrpc time: ', time.perf_counter() - start)
            return result
        except Exception as e:
            print(e)
            return str(e)

    def get_stock(self):
        try:
            start = time.perf_counter()
            if self.data:
                data = int(self.data)
                print(data)
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[['id', '=', data]]],
                    {'fields': ['name', 'qty_available',
                                'incoming_qty', 'outgoing_qty',
                                'virtual_available']}
                )
            else:
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[]], {'fields': ['name', 'qty_available', 'incoming_qty',
                                      'outgoing_qty', 'virtual_available']}
                )
            result = json.dumps(result)
            print('Get Stock xmlrpc time: ', time.perf_counter() - start)
            return result
        except Exception as e:
            print(e)
            return str(e)

    def list_cogs(self):
        try:
            start = time.perf_counter()
            if self.data:
                data = self.data
                print(data)
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[['id', 'in', data]]],
                    {'fields': ['name', 'qty_available', 'incoming_qty',
                                'outgoing_qty', 'virtual_available']}
                )
            else:
                result = self.models.execute_kw(
                    self.db, 2, 'admin', 'product.product', 'search_read',
                    [[]], {'fields': ['name', 'qty_available', 'incoming_qty',
                                      'outgoing_qty', 'virtual_available']}
                )
            result = json.dumps(result)
            print('Get COGS xmlrpc time: ', time.perf_counter() - start)
            return result
        except Exception as e:
            print(e)
            return str(e)
