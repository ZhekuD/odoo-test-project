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
        # search='_search_in_path'
        store=True,
    )
    parent_ids = fields.Many2many(
        comodel_name='openacademy.course',
        relation='ids',
        column1='child_id',
        column2='parent_id'
    )

    @api.constrains('parent_id')
    def _check_course_recursion(self):
        if not self._check_recursion():
            raise ValidationError  # (_('Error!'))
        return True

    @api.model
    def create(self, vals_list):
        created_obj = super().create(vals_list)
        if 'parent_id' in vals_list.keys():
            temp_obj = created_obj
            while temp_obj.parent_id:
                created_obj.parent_ids += temp_obj.parent_id
                temp_obj = object.parent_id
        return created_obj

    def write(self, vals):
        super().write(vals)
        if 'parent_id' in vals.keys():
            search_result = self.search([('id', 'child_of', self.id)])
            for record in search_result:
                object = record
                record.parent_ids = None
                while object.parent_id:
                    record.parent_ids += object.parent_id
                    object = object.parent_id

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
        # def create_path_string(obj):
        #     if obj.parent_id:
        #         return ' / '.join((obj.parent_id.parents_path, obj.name))
        #     else:
        #         return f'//{obj.name}'
        temp_self = self
        while temp_self.parent_id:
            self.parent_ids += temp_self.parent_id
            temp_self = temp_self.parent_id

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


class Sessions(models.Model):
    _name = 'openacademy.session'
    _description = 'OpenAcademy Sessions'

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(
        digits=(0, 2),
        help="bla bla bla"
    )
