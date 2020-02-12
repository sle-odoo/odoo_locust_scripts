``` bash
./odoo-bin -d 13.0 -i stock --without-demo all --stop-after-init

./odoo-bin shell -d 13.0 <<EOF
for i in ['A', 'B', 'C', 'D']:
    env['product.product'].create({
        'name': 'product'+i,
        'type': 'product',
    })

env['res.users'].create({
    'name': 'picker1',
    'login': 'picker1',
    'password': 'picker1',
})
env['res.users'].create({
    'name': 'picker2',
    'login': 'picker2',
    'password': 'picker2',
})
env.cr.commit()
EOF
```
