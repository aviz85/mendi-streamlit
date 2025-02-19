from services.nikud_service import NikudService

def test_nikud():
    service = NikudService()
    results = service.test()
    
    # Print test results
    for test_name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {test_name}")
    
    # Test remove_nikud
    text_with_nikud = "שָׁלוֹם"
    text_without_nikud = service.remove_nikud(text_with_nikud)
    print(f"\nRemove nikud test:")
    print(f"Input: {text_with_nikud}")
    print(f"Output: {text_without_nikud}")

if __name__ == "__main__":
    test_nikud() 