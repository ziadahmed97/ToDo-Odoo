from odoo import *

from Task1.odoo.exceptions import ValidationError


class TaskAssign(models.TransientModel):
    _name = 'task.assign'
    task_ids = fields.Many2one('todo',readonly=True)
    assignto_id = fields.Many2one('assignedto')

    def action_confirm(self):
            todos = self.task_ids
            if not todos:
                todos = self.env['todo'].browse(self._context.get('active_ids', []))
            if not todos:
                raise ValidationError("No tasks selected to assign.")
            invalid = todos.filtered(lambda t: t.status not in ('new', 'in_progress'))
            if invalid:
                statuses = set(invalid.mapped('status'))
                raise ValidationError(
                    "Cannot assign tasks with status(s): %s. Only 'new' or 'in_progress' allowed."
                    % (', '.join(statuses),)
                )
            todos.write({
                'assigned_to_id': self.assignto_id.id,
                'assigned_to': self.assignto_id.name,
            })
            return {'type': 'ir.actions.act_window_close'}

