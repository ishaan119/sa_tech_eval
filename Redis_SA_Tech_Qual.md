# Redis SA Tech Qualification Steps

This document outlines the steps performed for the technical qualification exercise.

## Part 1: Technical Exercise - Replica-of

### 1. Install standalone Open Source Redis version 3.0.7 on Server A

- **SSH into Server A:**
  ```bash
  ssh -i <path_to_pem_file> ubuntu@34.47.152.199
  ```
- **Download, Extract, and Compile Redis:**
  ```bash
  wget http://download.redis.io/releases/redis-3.0.7.tar.gz
  tar xzf redis-3.0.7.tar.gz
  cd redis-3.0.7
  make
  ```
  *(Screenshot: Terminal showing successful compilation)*

### 2. Configure Redis OSS

- **Modify redis.conf:**
  - Open the configuration file: `vi redis.conf`
  - Change the port from `6379` to `13379`.
  ```
  port 13379
  ```
- **Start Redis Server:**
  ```bash
  src/redis-server ./redis.conf
  ```
  *(Screenshot: Terminal showing Redis server running on the new port)*

### 3. Load Data with memtier-benchmark

- **Install memtier-benchmark dependencies:**
  ```bash
  sudo apt-get update
  sudo apt-get install -y build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev
  ```
- **Clone and build memtier-benchmark:**
  ```bash
  git clone https://github.com/RedisLabs/memtier_benchmark.git
  cd memtier_benchmark
  autoreconf -ivf
  ./configure
  make
  ```
- **Run benchmark to load data:**
  ```bash
  ./memtier_benchmark -s 34.47.152.199 -p 13379 --protocol=redis --requests=10000 --clients=5 --threads=2 --data-size=1024 --key-minimum=1 --key-maximum=10000 --key-pattern=S:S --ratio=1:0
  ```
  *(Screenshot: memtier_benchmark output showing data loading)*

### 4. Install Redis Enterprise on Server B

- **SSH into Server B:**
  ```bash
  ssh -i <path_to_pem_file> ubuntu@35.200.211.116
  ```
- **Download Redis Enterprise:**
  ```bash
  wget https://s3.amazonaws.com/redis-enterprise-software-downloads/5.4.0/redislabs-5.4.0-19-rhel7-x86_64.tar
  ```
- **Extract and Install:**
  ```bash
  tar vxf redislabs-5.4.0-19-rhel7-x86_64.tar
  cd redislabs-5.4.0-19
  sudo ./install.sh
  ```
  *(Screenshot: Installation progress and completion)*

### 5. Setup Redis Enterprise (No DNS)

- Access the Redis Enterprise web UI by navigating to `https://35.200.211.116:8443` in a browser.
- Proceed through the setup wizard, selecting the "no DNS" option when prompted.
- Complete the cluster configuration.
  *(Screenshot: Redis Enterprise setup screen)*

### 6. Create a Redis DB on Redis Enterprise

- In the Redis Enterprise UI, navigate to the "Databases" section.
- Click "Create Database" and configure a new Redis database.
  *(Screenshot: Database creation screen)*

### 7. Enable "Replica Of"

- In the configuration for the newly created Redis Enterprise DB, find the "Replica Of" setting.
- Enable it and provide the connection details for the source Redis OSS instance:
  - **Source:** `redis://34.47.152.199:13379`
- Save the configuration. The replication should start automatically.
  *(Screenshot: "Replica Of" configuration panel)*

### 8. Email Progress Update

- Send an email detailing the completion of the "Replica-of" section.

---

## Part 2: Application

### 1. Insert values 1-100 to Redis OSS

- **Language:** Python 3
- **Library:** `redis-py`
- **Script (`insert.py`):**
  ```python
  import redis

  # Connect to Redis OSS
  r = redis.Redis(host='34.47.152.199', port=13379, db=0)

  # Name for our list
  list_name = 'tech_qual_list'

  # Clear any old data in the list
  r.delete(list_name)

  # Insert numbers 1-100
  for i in range(1, 101):
      r.rpush(list_name, i)

  print(f"Inserted 100 values into '{list_name}' on Redis OSS.")

  # Validation: Print the list from OSS
  print("Values in Redis OSS:", r.lrange(list_name, 0, -1))
  ```
- **Execution and Output:**
  *(Screenshot: Terminal showing the output of `insert.py`)*

### 2. Extract values in reverse order from Redis Enterprise DB

- **Script (`extract.py`):**
  ```python
  import redis

  # Connect to Redis Enterprise DB
  # Note: The port will be provided in the Redis Enterprise UI endpoint
  re_host = '35.200.211.116'
  re_port = <DB_ENDPOINT_PORT> 
  r = redis.Redis(host=re_host, port=re_port, db=0)

  list_name = 'tech_qual_list'

  # Fetch the list
  values = r.lrange(list_name, 0, -1)

  # Decode from bytes and convert to int for sorting
  values = [int(v.decode('utf-8')) for v in values]

  # Reverse the list
  values.reverse()

  print(f"Extracted {len(values)} values from '{list_name}' on Redis Enterprise and reversed them.")
  print("Reversed values:", values)
  ```
- **Execution and Output:**
  *(Screenshot: Terminal showing the reversed list from 100 to 1)*

### 3. Validation

- The output from the `insert.py` script serves as the validation for step 1.
- The output from the `extract.py` script serves as the validation for step 2.
