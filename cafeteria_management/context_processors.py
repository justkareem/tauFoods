def menu_items(request):
    return {
        'menu_items': [
            {'name': 'Dashboard', 'url': 'dashboard', 'icon': 'ph-duotone ph-gauge'},
            {'name': 'Orders', 'url': 'orders', 'icon': 'ph-duotone ph-basket'},
            {'name': 'Food', 'url': 'food', 'icon': 'ph-duotone ph-bowl-food',
             'submenu': [
                 {'name': 'Add Food', 'url': 'add_food'},
                 {'name': 'Change Food Availability', 'url': 'update_food'}
             ]
             },
            {'name': 'Transactions', 'url': 'transactions', 'icon': 'ph-duotone ph-currency-ngn'},
            {'name': 'Announcement', 'url': 'send_announcement', 'icon': 'ph-duotone ph-megaphone'},
        ]
    }
