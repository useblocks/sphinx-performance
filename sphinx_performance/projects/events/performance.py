parameters = {
    "sphinx": "5.1",
    "dummies": 1,
    "pages": 1,
    "folders": 0,
    "depth": 1,
}

info = {
    "#dummies": "{{dummies * page_amount}}",
    "#pages": "{{page_amount}}",
    "#indexes": "{{index_amount}}",
    "#folders": "{{folders ** depth}}",
}

references = {
    "small": {
        "sphinx": "5.1",
        "dummies": 10,
        "pages": 10,
        "folders": 0,
        "depth": 1,
    },
    "medium": {
        "sphinx": "5.1",
        "dummies": 30,
        "pages": 20,
        "folders": 10,
        "depth": 1,
    },
    "large": {
        "sphinx": "5.1",
        "dummies": 30,
        "pages": 20,
        "folders": 10,
        "depth": 2,
    },
}
