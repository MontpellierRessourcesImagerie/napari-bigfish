from napari_bigfish import make_sample_data

# add your tests here...


def test_sample_data():
    data = make_sample_data()
    assert data[0][1]['name'] == 'spots (bigfish example image)'

