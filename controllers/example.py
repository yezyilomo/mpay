from odoo import http, api
from odoo.http import request

class Example(http.Controller):
    @http.route('/auth_usr', type='http', auth='public', website=True, )
    def render_example_page(self):
        return http.request.render("Mpay.example__page", {})

    @http.route('/method', type='http', auth='public', website=True, methods=['POST'])

    def post_method(self, **kw):
        data=request.env['received.transaction'].search([],limit=10)
        for i in data:
            print(i.sender_name)
        print ( '\n'+ kw['username']+'\n')
        print ( '\n'+ kw['password']+'\n')
        print ( '\n'+ kw['message']+'\n')
        return request.render("Mpay.posted_page",{'data':data})
