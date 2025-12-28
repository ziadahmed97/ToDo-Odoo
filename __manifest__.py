{
    "name" : "Task1",
    "author" : "Ziad Ahmed",
    "depends":['base','mail','web'],
    "data":['data/todo_sequence.xml',
            'security/security.xml'
        ,'security/ir.model.access.csv'
        ,'views/tasks_view.xml',
        'views/assigned_to_view.xml',
        'reports/todo_report.xml',
            'wizard/task_assigning.xml'

    ],
    "application": True,
}