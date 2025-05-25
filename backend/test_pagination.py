#!/usr/bin/env python3
"""
Simple test script to verify pagination implementation
"""
import requests
import json

def test_pagination():
    base_url = "http://localhost:8000"
    
    print("Testing pagination endpoints...")
    
    # Test 1: Basic pagination
    print("\n1. Testing basic pagination (page 1, size 5)")
    try:
        response = requests.get(f"{base_url}/testimonies?page=1&size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Got {len(data.get('items', []))} items")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Page: {data.get('page', 0)}")
            print(f"  Size: {data.get('size', 0)}")
            print(f"  Pages: {data.get('pages', 0)}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Different page size
    print("\n2. Testing different page size (page 1, size 10)")
    try:
        response = requests.get(f"{base_url}/testimonies?page=1&size=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Got {len(data.get('items', []))} items")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Page: {data.get('page', 0)}")
            print(f"  Size: {data.get('size', 0)}")
            print(f"  Pages: {data.get('pages', 0)}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Filtering with pagination
    print("\n3. Testing filtering with pagination (church_id filter)")
    try:
        response = requests.get(f"{base_url}/testimonies?page=1&size=5&church_id=Lausanne")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Got {len(data.get('items', []))} items for Lausanne")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Page: {data.get('page', 0)}")
            print(f"  Size: {data.get('size', 0)}")
            print(f"  Pages: {data.get('pages', 0)}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Status filtering with pagination
    print("\n4. Testing status filtering with pagination")
    try:
        response = requests.get(f"{base_url}/testimonies?page=1&size=5&transcript_status=completed")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Got {len(data.get('items', []))} completed testimonies")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Page: {data.get('page', 0)}")
            print(f"  Size: {data.get('size', 0)}")
            print(f"  Pages: {data.get('pages', 0)}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Default pagination (no parameters)
    print("\n5. Testing default pagination (no parameters)")
    try:
        response = requests.get(f"{base_url}/testimonies")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Got {len(data.get('items', []))} items with defaults")
            print(f"  Total: {data.get('total', 0)}")
            print(f"  Page: {data.get('page', 0)}")
            print(f"  Size: {data.get('size', 0)}")
            print(f"  Pages: {data.get('pages', 0)}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_pagination() 