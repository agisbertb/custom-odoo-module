{
    "name": "Complaints",  # The name that will appear in the App list
    "version": "1.0.0",  # Version
    "author": "Andreu Gisbert Bel & Ismael Semmar Gàlvez", # author
    "summary": "Customer complaints",  # A short description of the module
    "application": True,  # This line says the module is an App, and not a module
    "depends": ["base", "sale", "stock", "account"],  # The modules that this module depends on sale
    "data": [
        "security/ir.model.access.csv",
        "views/complaints_view.xml",
        "views/complaints_menu.xml",

    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    'license': 'LGPL-3',
}