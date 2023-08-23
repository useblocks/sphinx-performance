parameters = {
    "sphinx": "5.1",
    "dummies": 10,
    "pages": 10,
    "folders": 0,
    "depth": 1,
    "theme": "alabaster",
    "sidebar": 5,
}

info = {
    "#dummies": "{{dummies * page_amount}}",
    "#pages": "{{page_amount}}",
    "#indexes": "{{index_amount}}",
    "#folders": "{{folders ** depth}}",
}

references = {
    "alabaster": {
        "sphinx": "5.1",
        "dummies": 10,
        "pages": 10,
        "folders": 10,
        "depth": 1,
        "theme": "alabaster",
        "sidebar": 5,
    },
    "rtd": {
        "sphinx": "5.1",
        "dummies": 10,
        "pages": 10,
        "folders": 10,
        "depth": 1,
        "theme": "rtd",
        "sidebar": 5,
    },
    "pydata": {
        "sphinx": "5.1",
        "dummies": 10,
        "pages": 10,
        "folders": 10,
        "depth": 1,
        "theme": "pydata",
        "sidebar": 5,
    },
    "furo": {
        "sphinx": "5.1",
        "dummies": 10,
        "pages": 10,
        "folders": 10,
        "depth": 1,
        "theme": "furo",
        "sidebar": 5,
    },
}
