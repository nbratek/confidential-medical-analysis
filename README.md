# Confidential Medical Data Analysis

The hospital encrypts patient measurements with a CKKS public key and sends them to an external
server. The server computes statistics (mean, sum, RMS, variance) 
on ciphertexts, without seeing the raw values and returns the
encrypted result. Only the hospital can decrypt it.

## Natalia Bratek, Przemysław Popowski, Szymon Kubiczek



### Setup 

```bash
uv sync
```

### Running the Application

Open a terminal and run:

```bash
uv run python server.py
```

Open a second terminal and run:

```bash
uv run python client.py
```

### Example Usage

After launching the client, choose a metric:

```text
Select data to analyze:
 * 1 - bmi
 * 2 - body_temperature
 * 3 - cholesterol_hdl
....
```
You can enter the number

```text
> 1
```
Then choose a statistic to compute:

```text
Select statistic to compute:
 * 1 - Mean
 * 2 - Sum
 * 3 - Root Mean Square
 * 4 - Variance
 * q - Exit
```

The client stays active so you can compute multiple statistics on the
same encrypted vector without re-encrypting.

### Data

Patient data generated with: https://github.com/synthetichealth/synthea

### Homomorphic encryption
We use TenSEAL https://github.com/OpenMined/TenSEAL