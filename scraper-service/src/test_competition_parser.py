from competition_parser import extraer_identificadores_competicion


def test_extraer_identificadores_competicion():
    html = '''
    {
        "tournament_id":"0KangpCU",
        "tournamentId":"dtweQvIP"
    }
    '''

    resultado = extraer_identificadores_competicion(html)

    assert resultado["tournament_template_id"] == "0KangpCU"
    assert resultado["tournament_id"] == "dtweQvIP"


def test_error_si_no_hay_identificadores():
    html = "<html><body>Sin identificadores</body></html>"

    try:
        extraer_identificadores_competicion(html)
        assert False, "Se esperaba un ValueError"
    except ValueError:
        assert True
        