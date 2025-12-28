import json
from urllib.parse import parse_qs

from odoo import http
from odoo.http import request
import math
def valid_response(data,status,pagination_info):
    response_body= {
        "data" : data,
        "message" : "successful"
    }
    if pagination_info:
        response_body['pagination_info']=pagination_info
    return request.make_json_response(response_body,status=status)
def invalid_reponse(error,status):
    response_body = {
        "error" : error
    }
    return request.make_json_response(response_body,status=status)


class TodoApi(http.Controller):

    @http.route("/v1/todo/<int:todo_id>",methods=["GET"],type="http",auth='none',csrf=False)
    def todo_get(self,todo_id):
        try:
            todo_id= request.env['todo'].sudo().search([('id','=',todo_id)])
            if not todo_id:
                return request.make_json_response({
                    'error': 'Todo not found'
                }, status=404)
            return valid_response({
                    'todo_id':todo_id.id,
                    'name':todo_id.task_name,
                    'status':todo_id.status
                },200)
        except Exception as e:
            return invalid_reponse(e,400)

    @http.route("/v1/todo/", methods=["POST"], type="http", auth='none', csrf=False)
    def todo_post(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        try:
            if not vals.get('name'):
                return invalid_reponse("name is required",401)
            res = request.env['todo'].sudo().create(vals)
            if res:
                return valid_response({
                    "message":"new task has been added.",
                    'task_name': res.task_name,
                    'status': res.status
                },201)
        except Exception as e:
            return invalid_reponse(e,400)

    @http.route("/v1/todo/<int:todo_id>", methods=["PUT"], type="http", auth='none', csrf=False)
    def todo_put(self,todo_id):
        try:
            todo_id = request.env['todo'].sudo().search([('id','=',todo_id)])
            if not todo_id:
                return invalid_reponse("ID does not exist",400)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            todo_id.write(vals)
            return valid_response({
                "message" : "Task has been updated",
                "name" : todo_id.task_name,
                "status" : todo_id.status

            },201)
        except Exception as e:
            return invalid_reponse(e,400)

    @http.route("/v1/todo/<int:todo_id>", methods=["DELETE"], type="http", auth='none', csrf=False)
    def todo_unlink(self,todo_id):
        try:
            todo_id = request.env['todo'].sudo().search([('id','=',todo_id)])
            if not todo_id:
                return invalid_reponse("ID does not exist to be deleted", 400)
            todo_id.unlink()
            return valid_response({"message":"The task has been deleted successfully"},201)
        except Exception as e:
            return invalid_reponse(e,400)

    @http.route("/v1/todo/tasks", methods=["GET"], type="http", auth='none', csrf=False)
    def get_all_tasks(self):
        try:
            parms = parse_qs(request.httprequest.query_string.decode('utf-8'))
            todo_domain = []
            page = offset = None
            limit = 0
            if parms:
                if parms.get('page'):
                    page = int(parms.get('page')[0])
                if parms.get('limit'):
                    limit= int(parms.get('limit')[0])
            if page:
                offset = (page * limit) - limit
            if parms.get('status'):
                todo_domain += [('status','=',parms.get('status')[0])]
            todo_ids = request.env['todo'].sudo().search(todo_domain,limit=limit,offset=offset,order='id asc')

            todo_count =request.env['todo'].sudo().search_count(todo_domain)
            # todo_ids = request.env['todo'].sudo().search([])
            if not todo_ids:
                return invalid_reponse("No Records to be displayed.",400)

            return valid_response([{
                "id" : task.id,
                "task_name":task.task_name,
                "status": task.status
            }for task in todo_ids],201,pagination_info={
                'page': page if page else 1,
                'limit': limit,
                'pages': math.ceil(todo_count / limit) if limit else 1,
                'count': todo_count
            })

        except Exception as e:
            return invalid_reponse(e,400)
