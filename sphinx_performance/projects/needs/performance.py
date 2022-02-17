parameters = {
    "sphinx": "4.2",
    "needs": 10,
    "needtables": 2,
    "dummies": 10,
    "pages": 10,
    "folders": 0,
    "depth": 1
}

info = {
    "#needs": "{{needs * page_amount}}",
    "#needtables": "{{needtables * page_amount}}",
    "#dummies": "{{dummies * page_amount}}",
    '#pages': "{{page_amount}}",
    '#indexes': "{{index_amount}}",
    '#folders': "{{folders ** depth}}"
}
