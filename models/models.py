# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slugify
import logging

logger = logging.getLogger("MODEL_APP")
logger.setLevel(logging.INFO)

class Course(models.Model):
    _name = 'openacademy.course'
    _description = "OpenAcademy Courses"
    _paren_name = 'parent_id'

    name = fields.Char(string="Title", required=True)
    url = fields.Char()
    description = fields.Text()
    product_status = fields.Selection(
        string='Communication',
        selection=[
            ('created', 'Choise 1'),
            ('inprogress', 'Choise 2'),
            ('done', 'Choise 3'),
        ],
        default='created',
    )
    parent_id = fields.Many2one(comodel_name='openacademy.course')
    parents_path = fields.Char(
        compute='parent_path_string',
        default='/',
        search='_search_in_path'
        # store=True,
    )
    parent_ids = fields.Many2many(
        comodel_name='openacademy.course',
        relation='ids',
        column1='child_id',
        column2='parent_id'
    )

    def write(self, vals):
        super().write(vals)

    @api.depends('parent_id', 'parents_path')
    def parent_path_string(self):
        for record in self:
            if not record.parent_id:
                name = record.name if record.name else ''
                record.parents_path = '/ ' + name
            else:
                record.parents_path = str(record.parent_id.parents_path) + \
                    ' / ' + record.name

    def recalculate_parents(self):
        pass
        logger.info('---------->')
        logger.info(str(self.ids))

    def next_status(self):
        if self.product_status == 'created':
            self.product_status = 'inprogress'
        elif self.product_status == 'inprogress':
            self.product_status = 'done'

    def prev_status(self):
        if self.product_status == 'inprogress':
            self.product_status = 'created'
        elif self.product_status == 'done':
            self.product_status = 'inprogress'

    @api.onchange('name')
    def _name_to_url(self):
        if self.name:
            self.url = slugify(self.name)

    def _search_in_path(self, operator, value):
        recs = self.search([]).filtered(lambda x: value in x.parents_path)
        result = recs.ids if recs.ids else ()
        logger.info('---------->')
        logger.info(str(self.ids))
        return [('id', 'in', result)]



#
# class ParentsPathModel():
#     _name = 'parents_path_model'



class Sessions(models.Model):
    _name = 'openacademy.session'
    _description = 'OpenAcademy Sessions'

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(
        digits=(0, 2),
        help="bla bla bla"
    )
