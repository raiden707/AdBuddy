import data_layer

def test_datalayer():

    duckpile_UID = 6350
    good_username = "duckpile"
    bad_username = "duckpile1"

    assert data_layer.pull_id(good_username) == duckpile_UID
    assert data_layer.pull_id(bad_username) == False

