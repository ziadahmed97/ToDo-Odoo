import requests
from odoo import fields,models,api
from odoo.api import Self


from Task1.odoo.exceptions import ValidationError


class Todo(models.Model):
    _name = "todo"
    _description = "To-Do Task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'task_name'
    active = fields.Boolean(default=True)
    ref = fields.Text()
    task_name = fields.Char(required=1)
    assigned_to = fields.Char()
    description = fields.Text()
    due_date= fields.Date()
    is_late = fields.Boolean()
    status = fields.Selection([
        ('new','New'),
        ('in_progress','In Progress'),
        ('completed','Completed'),
        ('close','Close')
    ],default='new')
    estimated_time = fields.Float()
    total_time = fields.Float(compute='_compute_total_time')
    assigned_to_id = fields.Many2one('assignedto')

    line_ids = fields.One2many('todo.lines','line_id')

    @api.model
    def create(self, vals_list) -> Self:
        res = super(Todo, self).create(vals_list)
        res.ref = self.env['ir.sequence'].next_by_code('todo_sequence')
        return res

    @api.depends('line_ids.time')
    def _compute_total_time(self):
        for rec in self:
            rec.total_time = sum(line.time for line in rec.line_ids)

    @api.constrains('line_ids', 'estimated_time')
    def _check_estimated_time(self):
        for rec in self:
            if rec.estimated_time and rec.total_time > rec.estimated_time:
                raise ValidationError(
                    "Total time of lines (%.2f) exceeds the estimated time (%.2f)."
                    % (rec.total_time, rec.estimated_time)
                )

    def action_new(self):
        for rec in self:
            rec.write(
                {
                    'status':'new'
                }
            )

    def action_in_progress(self):
        for rec in self:
            rec.write({
                'status':'in_progress'
            })
    def action_completed(self):
        for rec in self:
            rec.write({
                'status':'completed'
            })

    # def action_closed(self):
    #     for rec in self:
    #         rec.write({
    #             'status':'close'
    #         })
    def close_state_action(self):
        for rec in self:
            rec.status = 'close'
    def due_date_exceeded_action(self):
        today = fields.Date.today()
        overdue = self.search([('due_date','>',today),('status' ,'in',('new','in_progress') )])
        for rec in overdue:
            rec.is_late = True
    def action_open_task_assign_wizard(self):
            action = self.env['ir.actions.actions']._for_xml_id('TaskOne.task_assign_action')
            action['context'] = {'default_task_ids': [(6, 0, self.ids)]}
            return action
    def get_todo_from_external_app(self):
        payload=dict()
        try:
            page = 1
            limit = 5
            response = requests.get(f"http://127.0.0.1:8069/v1/todo/tasks?page={page}&limit={limit}",data=payload)
            if response.status_code==201:
                data = response.json()
                tasks = data['data']
                for task in tasks:
                    print(f"The Task Name is: {task['task_name']}")
                print(data['pagination_info'])
        except Exception as e:
            raise ValidationError(str(e))



class TodoLines(models.Model):
    _name = 'todo.lines'
    _description = 'To-Do Task Line'

    date = fields.Date()
    description = fields.Text()
    time = fields.Float()

    line_id = fields.Many2one('todo', string="Todo")

    @api.model
    def create(self, vals):
        res = super(TodoLines, self).create(vals)
        res._check_parent_time_limit()
        return res

    def write(self, vals):
        res = super(TodoLines, self).write(vals)
        for rec in self:
            rec._check_parent_time_limit()
        return res

    def _check_parent_time_limit(self):

        for rec in self:
            parent = rec.line_id
            if not parent:
                continue
            total = sum(line.time or 0.0 for line in parent.line_ids)
            if parent.estimated_time and total > parent.estimated_time:
                raise ValidationError(
                    "Total time of lines (%.2f) exceeds the estimated time (%.2f) "
                    "for task '%s'." % (total, parent.estimated_time, parent.task_name or parent.id)
                )