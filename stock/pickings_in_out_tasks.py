from OdooLocust.OdooLocust import OdooLocust
from locust import task, TaskSet, between

import random


class PickerTaskSet(TaskSet):
    def _prepare_move_vals(self, product, qty, picking, location, location_dest):
        return {
            'product_id': product,
            'product_uom_qty': qty,
            'picking_id': picking,
            'location_id': location,
            'location_dest_id': location_dest,
            'name': 'locust move',
            'product_uom': 1,  # hardcode units uom
        }

class PickerOutTaskSet(PickerTaskSet):
    """Delivery picker task set"""
    @task(1)
    def create_out_picking(self):
        stock_move_model = self.client.get_model('stock.move')
        product_product_model = self.client.get_model('product.product')
        picking_model = self.client.get_model('stock.picking')
        location_model = self.client.get_model('stock.location')
        picking_type_model = self.client.get_model('stock.picking.type')
        parter_model = self.client.get_model('res.partner')

        customer_location = location_model.search([
            ('usage', '=', 'customer'),
        ], limit=1)[0]
        stock_location = location_model.search([
            ('usage', '=', 'internal'),
            ('company_id', '=', 1)
        ], limit=1)[0]
        picking_type_out = picking_type_model.search([
            ('code', '=', 'outgoing'),
            ('company_id', '=', 1)
        ], limit=1)[0]
        picking_out = picking_model.create({
            'picking_type_id': picking_type_out,
            'location_id': stock_location,
            'location_dest_id': customer_location,
        })
        product = product_product_model.search([])
        move_vals = []
        for i in range(50):
            # we choose 50 product randomly to spread the reservation accross
            # all product and reduce the table locks
            product_id = random.choice(product)
            move_vals.append(self._prepare_move_vals(product_id, 5, picking_out, stock_location, customer_location))
        stock_move_model.create(move_vals)

        picking_model.action_confirm(picking_out)
        picking_model.action_assign(picking_out)
        moves = stock_move_model.search([('picking_id', '=', picking_out)])
        stock_move_model.write(moves, {'quantity_done': 5})
        picking_model.action_done(picking_out)


class PickerInTaskSet(PickerTaskSet):
    """Reception picker task set"""
    @task(1)
    def create_in_picking(self):
        stock_move_model = self.client.get_model('stock.move')
        product_product_model = self.client.get_model('product.product')
        picking_model = self.client.get_model('stock.picking')
        location_model = self.client.get_model('stock.location')
        picking_type_model = self.client.get_model('stock.picking.type')

        supplier_location = location_model.search([
            ('usage', '=', 'supplier'),
        ], limit=1)[0]
        stock_location = location_model.search([
            ('usage', '=', 'internal'),
            ('company_id', '=', 1)
        ], limit=1)[0]
        picking_type_in = picking_type_model.search([
            ('code', '=', 'incoming'),
            ('company_id', '=', 1)
        ], limit=1)[0]
        picking_in = picking_model.create({
            'picking_type_id': picking_type_in,
            'location_id': supplier_location,
            'location_dest_id': stock_location,
        })
        product = product_product_model.search([])
        move_vals = []
        for i in range(100):
            move_vals.append(self._prepare_move_vals(product[i], 5, picking_in, supplier_location, stock_location))
        stock_move_model.create(move_vals)

        picking_model.action_confirm(picking_in)
        moves = stock_move_model.search([('picking_id', '=', picking_in)])
        stock_move_model.write(moves, {'quantity_done': 5})
        picking_model.action_done(picking_in)


class PickerIn(OdooLocust):
    """Receipt picker"""
    host = "localhost"
    database = "13.0"
    login = "picker1"
    password = "picker1"
    wait_time = between(5, 10)
    weight = 3

    task_set = PickerInTaskSet


class PickerOut(OdooLocust):
    """Delivery picker"""
    host = "localhost"
    database = "13.0"
    login = "picker2"
    password = "picker2"
    wait_time = between(5.0, 10.0)
    weight = 3

    task_set = PickerOutTaskSet
