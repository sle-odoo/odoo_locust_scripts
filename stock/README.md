``` bash
./odoo-bin -d 13.0 -i stock --without-demo all --stop-after-init

./odoo-bin shell -d 13.0 <<EOF
for i in range(100):
    env['product.product'].create({
        'name': 'product'+str(i),
        'type': 'product',
    })
env['res.users'].create({
    'name': 'picker1',
    'login': 'picker1',
    'password': 'picker1',
    'email': 'picker1@example.com',
})
env['res.users'].create({
    'name': 'picker2',
    'login': 'picker2',
    'password': 'picker2',
    'email': 'picker2@example.com',
})
env.cr.commit()
EOF

locust -f pickings_in_out_tasks.py PickerIn PickerOut
```
