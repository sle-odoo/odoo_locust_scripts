from OdooLocust.OdooLocust import OdooLocust
from locust import task, TaskSet, between


class PickerTaskSet(TaskSet):
    """Common code for picker task set"""
    def _prepare_move_vals(self, product, qty, picking, location, location_dest):
        product_product_model = self.client.get_model('product.product')
        return {
            'name': product_product_model.read(product)['name'],
            'product_id': product,
            'product_uom_qty': qty,
            'product_uom': product_product_model.read(product)['uom_id'][0],
            'picking_id': picking,
            'location_id': location,
            'location_dest_id': location_dest
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
        productA = product_product_model.search([('name', '=', 'productA')])[0]
        productB = product_product_model.search([('name', '=', 'productB')])[0]
        productC = product_product_model.search([('name', '=', 'productC')])[0]
        productD = product_product_model.search([('name', '=', 'productD')])[0]
        move_a = stock_move_model.create(self._prepare_move_vals(productA, 5, picking_out, stock_location, customer_location))
        move_b = stock_move_model.create(self._prepare_move_vals(productB, 1, picking_out, stock_location, customer_location))
        move_c = stock_move_model.create(self._prepare_move_vals(productC, 10, picking_out, stock_location, customer_location))
        move_d = stock_move_model.create(self._prepare_move_vals(productD, 10, picking_out, stock_location, customer_location))

        picking_model.action_confirm(picking_out)
        picking_model.action_assign(picking_out)
        for move in stock_move_model.search([('picking_id', '=', picking_out)]):
            qty = stock_move_model.read(move)['product_uom_qty']
            stock_move_model.write(move, {'quantity_done': qty})
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
        productA = product_product_model.search([('name', '=', 'productA')])[0]
        productB = product_product_model.search([('name', '=', 'productB')])[0]
        productC = product_product_model.search([('name', '=', 'productC')])[0]
        productD = product_product_model.search([('name', '=', 'productD')])[0]
        move_a = stock_move_model.create(self._prepare_move_vals(productA, 5, picking_in, supplier_location, stock_location))
        move_b = stock_move_model.create(self._prepare_move_vals(productB, 1, picking_in, supplier_location, stock_location))
        move_c = stock_move_model.create(self._prepare_move_vals(productC, 10, picking_in, supplier_location, stock_location))
        move_d = stock_move_model.create(self._prepare_move_vals(productD, 10, picking_in, supplier_location, stock_location))

        picking_model.action_confirm(picking_in)
        for move in stock_move_model.search([('picking_id', '=', picking_in)]):
            qty = stock_move_model.read(move)['product_uom_qty']
            stock_move_model.write(move, {'quantity_done': qty})
        picking_model.action_done(picking_in)


class PickerIn(OdooLocust):
    """Receipt picker"""
    host = "localhost"
    database = "13.0"
    login = "picker1"
    password = "picker1"
    wait_time = between(1.0, 2.0)
    weight = 3

    task_set = PickerInTaskSet


class PickerOut(OdooLocust):
    """Delivery picker"""
    host = "localhost"
    database = "13.0"
    login = "picker2"
    password = "picker2"
    wait_time = between(1.0, 2.0)
    weight = 3

    task_set = PickerOutTaskSet

