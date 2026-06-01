
import sys
import os
import io

# Force UTF-8 encoding for stdout/stderr on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import ReActAgent
from server.api import MockReActProvider
from src.agent.academic_tools import ACADEMIC_TOOLS as TOOLS

def main():
    print("Testing agent with MockReActProvider and academic tools")
    print("Query: find grades for S002")
    llm = MockReActProvider()
    agent = ReActAgent(llm=llm, tools=list(TOOLS.values()), max_steps=5)
    result = agent.run("tìm điểm của bạn S002 lớp 11")
    print("Agent History:")
    import json
    for step in agent.history:
        print(json.dumps(step, ensure_ascii=False, indent=2))
    print("\nFinal Answer:", result)

if __name__ == "__main__":
    main()

