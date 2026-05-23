"""Asynchronous test script for PiKVM API Client."""
import asyncio
import os
import sys

# Ensure pikvm_custom directory is in path for direct import to bypass HA package dependency
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "custom_components", "pikvm_custom")))

from client import PiKVMClient, PiKVMAuthError, PiKVMConnectionError

async def test_flow() -> None:
    """Test entire client API flow against local mock server."""
    host = "http://127.0.0.1:8080"
    username = "admin"
    password = "password"

    print("=== Testing Client against Mock Server ===")
    
    print("\n1. Initializing PiKVMClient...")
    client = PiKVMClient(host=host, username=username, password=password)

    try:
        print("2. Checking Connection (Valid Credentials)...")
        connected = await client.check_connection()
        print(f"   Success: {connected}")

        print("3. Fetching Initial ATX State...")
        state = await client.get_atx_state()
        print(f"   Initial State: {state}")
        
        print("4. Sending Click Power Button...")
        click_success = await client.click_button("power")
        print(f"   Click Success: {click_success}")

        print("5. Re-fetching ATX State to verify toggle...")
        toggled_state = await client.get_atx_state()
        print(f"   Toggled State: {toggled_state}")

        print("6. Sending Power Long Press (off_hard)...")
        action_success = await client.set_power_action("off_hard")
        print(f"   Action Success: {action_success}")

        print("7. Re-fetching ATX State to verify off state...")
        off_state = await client.get_atx_state()
        print(f"   Off State: {off_state}")

        # Test auth error handling
        print("\n8. Testing Client Auth Failure Handling...")
        bad_client = PiKVMClient(host=host, username="admin", password="wrongpassword")
        try:
            await bad_client.check_connection()
            print("   ERROR: Connection succeeded with wrong password!")
        except PiKVMAuthError:
            print("   Success: Auth error correctly raised and handled.")
        except Exception as err:
            print(f"   ERROR: Unexpected error raised: {err}")

    except PiKVMClientError as err:
        print(f"\n   CRITICAL FAILURE: API Client error occurred: {err}")
    finally:
        # Close the underlying aiohttp session
        await client._session.close()

if __name__ == "__main__":
    asyncio.run(test_flow())
