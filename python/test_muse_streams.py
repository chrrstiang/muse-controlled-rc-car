"""
Test script to see what streams Muse provides.
"""

from pylsl import resolve_streams
import time

print("=== Searching for all LSL streams ===\n")
print("Make sure 'muselsl stream --acc' is running...\n")

# Find all streams
streams = resolve_streams(wait_time=5.0)

if not streams:
    print("No streams found!")
    print("Make sure to run: muselsl stream --acc")
    exit()

print(f"Found {len(streams)} stream(s):\n")

for i, stream in enumerate(streams):
    print(f"Stream {i+1}:")
    print(f"  Name: {stream.name()}")
    print(f"  Type: {stream.type()}")
    print(f"  Channel Count: {stream.channel_count()}")
    print(f"  Sampling Rate: {stream.nominal_srate()} Hz")
    print(f"  Source ID: {stream.source_id()}")