
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.agent.academic_tools import get_academic_grades

print("Testing get_academic_grades with S002...")
result = get_academic_grades("S002")
print(result)
