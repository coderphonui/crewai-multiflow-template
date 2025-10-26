#!/usr/bin/env python
"""
Example script demonstrating how to interact with the CrewAI Flow API.
"""
import time
import requests
from typing import Optional


API_BASE_URL = "http://127.0.0.1:8000"


def trigger_poem_flow(sentence_count: Optional[int] = None) -> str:
    """
    Trigger a poem flow execution.
    
    Args:
        sentence_count: Optional number of sentences (1-10)
        
    Returns:
        Execution ID
    """
    url = f"{API_BASE_URL}/api/v1/poem-flow/execute"
    
    payload = {}
    if sentence_count is not None:
        payload["sentence_count"] = sentence_count
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    execution_id = data["execution_id"]
    
    print(f"✓ Flow execution triggered!")
    print(f"  Execution ID: {execution_id}")
    print(f"  Status: {data['status']}")
    
    return execution_id


def get_execution_status(execution_id: str) -> dict:
    """
    Get the status of a flow execution.
    
    Args:
        execution_id: The execution ID
        
    Returns:
        Execution status data
    """
    url = f"{API_BASE_URL}/api/v1/poem-flow/execution/{execution_id}"
    
    response = requests.get(url)
    response.raise_for_status()
    
    return response.json()


def wait_for_completion(execution_id: str, max_wait: int = 300, poll_interval: int = 2) -> dict:
    """
    Wait for a flow execution to complete.
    
    Args:
        execution_id: The execution ID
        max_wait: Maximum time to wait in seconds
        poll_interval: Time between status checks in seconds
        
    Returns:
        Final execution status data
    """
    print(f"\n⏳ Waiting for execution {execution_id} to complete...")
    
    elapsed = 0
    while elapsed < max_wait:
        status_data = get_execution_status(execution_id)
        status = status_data["status"]
        
        print(f"  [{elapsed}s] Status: {status}")
        
        if status == "completed":
            print("✓ Execution completed successfully!")
            return status_data
        elif status == "failed":
            print(f"✗ Execution failed: {status_data.get('error', 'Unknown error')}")
            return status_data
        
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    print(f"⚠ Timeout: Execution did not complete within {max_wait} seconds")
    return get_execution_status(execution_id)


def list_executions(status: Optional[str] = None, limit: int = 10):
    """
    List flow executions.
    
    Args:
        status: Filter by status (pending, running, completed, failed)
        limit: Maximum number of results
    """
    url = f"{API_BASE_URL}/api/v1/poem-flow/executions"
    
    params = {"limit": limit}
    if status:
        params["status"] = status
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    executions = response.json()
    
    print(f"\n📋 Found {len(executions)} execution(s):")
    for exec_data in executions:
        print(f"\n  ID: {exec_data['execution_id']}")
        print(f"  Status: {exec_data['status']}")
        print(f"  Created: {exec_data['created_at']}")
        if exec_data.get('result'):
            result = exec_data['result']
            print(f"  Sentences: {result.get('sentence_count')}")
            poem = result.get('poem', '')
            preview = poem[:100] + "..." if len(poem) > 100 else poem
            print(f"  Poem: {preview}")


def main():
    """Main example workflow."""
    print("=" * 60)
    print("CrewAI Flow API Example")
    print("=" * 60)
    
    try:
        # 1. Check API health
        print("\n1. Checking API health...")
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        print("   ✓ API is healthy")
        
        # 2. Trigger a flow execution
        print("\n2. Triggering poem flow execution...")
        execution_id = trigger_poem_flow(sentence_count=3)
        
        # 3. Wait for completion
        print("\n3. Waiting for completion...")
        result = wait_for_completion(execution_id, max_wait=120)
        
        # 4. Display results
        if result["status"] == "completed" and result.get("result"):
            print("\n4. Results:")
            print(f"   Sentence Count: {result['result']['sentence_count']}")
            print(f"   Poem:\n{'-' * 60}")
            print(result['result']['poem'])
            print('-' * 60)
        
        # 5. List all executions
        print("\n5. Listing recent executions...")
        list_executions(limit=5)
        
        print("\n" + "=" * 60)
        print("✓ Example completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("  Make sure the server is running: python run_api.py")
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
