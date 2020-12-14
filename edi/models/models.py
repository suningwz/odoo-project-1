# -*- coding: utf-8 -*-

from odoo import models, fields, api


class edi(models.Model):
    _name = 'edi.edi'
    _description = 'edi.edi'

    def get_all_so():
        # sql = "select * from product.template"
        # self.env.cr.execute(sql)
        # res_all = self.env.cr.fetchall()
        # # fetchall() will return an array of dictionaries
        # return res_all
        print('xxxxx')
