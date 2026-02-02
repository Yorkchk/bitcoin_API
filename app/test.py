import pyodbc
import sys

print(f"Python version: {sys.version}")
print("Installed ODBC Drivers:")
for driver in pyodbc.drivers():
    print(f" - {driver}")