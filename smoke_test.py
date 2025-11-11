#!/usr/bin/env python3
"""
Smoke Test - Verifikasi end-to-end untuk semua protokol
Memastikan semua protokol berfungsi dengan baik
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import time
import json
import logging
from datetime import datetime

# Import protocol clients
import paho.mqtt.client as mqtt
import requests
import aiocoap

from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SmokeTest')


class TestResult:
    """Hasil test"""
    def __init__(self, protocol, passed, message, duration=0):
        self.protocol = protocol
        self.passed = passed
        self.message = message
        self.duration = duration


def test_mqtt():
    """Test MQTT publish-subscribe"""
    logger.info("Testing MQTT...")
    
    broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
    port = int(os.getenv('MQTT_PORT', 1883))
    topic = 'IOTS/TEST/smoke'
    
    received_message = []
    
    def on_message(client, userdata, msg):
        received_message.append(msg.payload.decode('utf-8'))
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(topic)
    
    try:
        start_time = time.time()
        
        # Setup subscriber
        sub_client = mqtt.Client(client_id="smoke_test_sub")
        sub_client.on_connect = on_connect
        sub_client.on_message = on_message
        sub_client.connect(broker_host, port, keepalive=60)
        sub_client.loop_start()
        
        # Wait for subscription
        time.sleep(1)
        
        # Setup publisher
        pub_client = mqtt.Client(client_id="smoke_test_pub")
        pub_client.connect(broker_host, port, keepalive=60)
        pub_client.loop_start()
        
        # Publish test message
        test_data = {
            "device_id": "smoke_test",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        test_message = json.dumps(test_data)
        
        result = pub_client.publish(topic, test_message, qos=1)
        result.wait_for_publish(timeout=5)
        
        # Wait for message reception
        timeout = 5
        elapsed = 0
        while not received_message and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1
        
        duration = time.time() - start_time
        
        # Cleanup
        pub_client.loop_stop()
        pub_client.disconnect()
        sub_client.loop_stop()
        sub_client.disconnect()
        
        # Verify
        if received_message:
            received_data = json.loads(received_message[0])
            if received_data.get('device_id') == 'smoke_test':
                return TestResult('MQTT', True, 
                                "Message published and received successfully", duration)
            else:
                return TestResult('MQTT', False, 
                                "Received message content mismatch", duration)
        else:
            return TestResult('MQTT', False, 
                            "Message not received within timeout", duration)
        
    except Exception as e:
        return TestResult('MQTT', False, f"Error: {str(e)}")


def test_http():
    """Test HTTP request-response"""
    logger.info("Testing HTTP...")
    
    host = os.getenv('HTTP_HOST', 'localhost')
    port = int(os.getenv('HTTP_PORT', 8080))
    base_url = f"http://{host}:{port}"
    
    try:
        start_time = time.time()
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            return TestResult('HTTP', False, 
                            f"Health check failed: {response.status_code}")
        
        # Test ingest endpoint
        test_data = {
            "device_id": "smoke_test",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        
        response = requests.post(
            f"{base_url}/ingest",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                return TestResult('HTTP', True, 
                                "Request sent and response received successfully", 
                                duration)
            else:
                return TestResult('HTTP', False, 
                                f"Unexpected response: {response_data}")
        else:
            return TestResult('HTTP', False, 
                            f"Request failed: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        return TestResult('HTTP', False, "Connection failed - is server running?")
    except Exception as e:
        return TestResult('HTTP', False, f"Error: {str(e)}")


async def test_coap_async():
    """Test CoAP request-response (async)"""
    logger.info("Testing CoAP...")
    
    host = os.getenv('COAP_HOST', 'localhost')
    port = int(os.getenv('COAP_PORT', 5683))
    resource = '/telemetry'
    server_uri = f"coap://{host}:{port}{resource}"
    
    try:
        start_time = time.time()
        
        # Create context
        context = await aiocoap.Context.create_client_context()
        
        # Prepare test data
        test_data = {
            "device_id": "smoke_test",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        
        # Create request
        request = aiocoap.Message(
            code=aiocoap.POST,
            payload=json.dumps(test_data).encode('utf-8'),
            uri=server_uri
        )
        request.mtype = aiocoap.NON
        
        # Send request
        response = await context.request(request).response
        
        duration = time.time() - start_time
        
        # Cleanup
        await context.shutdown()
        
        # Verify
        if response.code.is_successful():
            try:
                response_data = json.loads(response.payload.decode('utf-8'))
                if response_data.get('status') == 'success':
                    return TestResult('CoAP', True, 
                                    "Request sent and response received successfully", 
                                    duration)
                else:
                    return TestResult('CoAP', False, 
                                    f"Unexpected response: {response_data}")
            except:
                return TestResult('CoAP', True, 
                                "Response received (parsing failed)", duration)
        else:
            return TestResult('CoAP', False, 
                            f"Request failed: {response.code}")
        
    except Exception as e:
        return TestResult('CoAP', False, f"Error: {str(e)}")


def test_coap():
    """Test CoAP (wrapper for async)"""
    return asyncio.run(test_coap_async())


def print_result(result):
    """Print test result dengan format yang bagus"""
    status_symbol = "✓" if result.passed else "✗"
    status_text = "PASS" if result.passed else "FAIL"
    
    color_code = "\033[92m" if result.passed else "\033[91m"  # Green or Red
    reset_code = "\033[0m"
    
    print(f"\n{color_code}[{status_symbol}] {result.protocol}: {status_text}{reset_code}")
    print(f"    Message: {result.message}")
    if result.duration > 0:
        print(f"    Duration: {result.duration:.3f}s")


def main():
    """Main function"""
    print("="*70)
    print("IoT Protocol Smoke Test")
    print("="*70)
    print("\nVerifying end-to-end functionality for all protocols...\n")
    
    results = []
    
    # Test MQTT
    try:
        result = test_mqtt()
        results.append(result)
        print_result(result)
    except Exception as e:
        result = TestResult('MQTT', False, f"Test crashed: {str(e)}")
        results.append(result)
        print_result(result)
    
    # Test HTTP
    try:
        result = test_http()
        results.append(result)
        print_result(result)
    except Exception as e:
        result = TestResult('HTTP', False, f"Test crashed: {str(e)}")
        results.append(result)
        print_result(result)
    
    # Test CoAP
    try:
        result = test_coap()
        results.append(result)
        print_result(result)
    except Exception as e:
        result = TestResult('CoAP', False, f"Test crashed: {str(e)}")
        results.append(result)
        print_result(result)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count
    
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    
    if failed_count == 0:
        print("\n✓ All tests passed!")
        print("="*70)
        return 0
    else:
        print("\n✗ Some tests failed. Please check the logs.")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
