parameters = {
    "sphinx": "4.1",
    "needs": 10,
    "needtables": 2,
    "pages": 10,
    "dummies": 10
}

info = {
    "#needs": "{{needs * pages}}",
    "#needtables": "{{needtables * pages}}",
    "#dummies": "{{dummies * pages}}"
}
