from odoo import *

class AssignedTo(models.Model):
    _name = "assignedto"
    name= fields.Char()
    to_do_ids = fields.One2many('todo','assigned_to_id')

