{
    "name": "Reclamations",  # The name that will appear in the App list
    "version": "1.0.0",  # Version
    "author": "Andreu Gisbert Bel & Ismael Semmar Gàlvez", # author
    "summary": "Customer complaints",  # A short description of the module
    "application": True,  # This line says the module is an App, and not a module
    "depends": ["base"],  # dependencies
    "data": [
        "security/ir.model.access.csv",
        "views/reclamation_view.xml",
        "views/reclamation_menu.xml",

    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    'license': 'LGPL-3',
}