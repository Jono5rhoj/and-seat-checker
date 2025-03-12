import random

# Other existing imports
import time

# Existing code...

while True:
    # Check seat availability logic...

    random_interval = random.randint(1800, 3600)  # Random wait time between 30 to 60 minutes
    print(f"Waiting for {random_interval // 60} minutes before next check...")
    time.sleep(random_interval)
