from services.nikud_mapper import NikudMapper

def test_nikud():
    mapper = NikudMapper()
    mapper.test_known_dataset()

if __name__ == "__main__":
    test_nikud()