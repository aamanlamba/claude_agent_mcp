
import subprocess
import sys
import time
import os
import threading
import queue

def enqueue_output(out, q):
    for line in iter(out.readline, b''):
        q.put(line)
    out.close()

def run_test():
    # Ensure we are in the correct directory
    cwd = "/Users/aamanlamba/Code/claude_agent_mcp"
    
    print(f"Starting agent.py in {cwd}...")
    process = subprocess.Popen(
        [sys.executable, "agent.py"],
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0 # Unbuffered
    )

    try:
        # Give it some time to start and connect to server
        print("Waiting for agent to initialize...")
        
        # We need to read stdout in a non-blocking way to check for prompts
        # but for simplicity in this short test, we can just write to stdin and read lines.
        # However, agent.py uses `input()` which prints prompt to stdout but doesn't flush? 
        # Actually `input()` writes to stdout.
        
        # Let's interact
        inputs = [
            "What is 50 + 25?",
            "Reverse the word 'testing'",
            "Generate a UUID",
            "Count words in 'The quick brown fox'",
            "quit"
        ]
        
        expected_outputs = [
            "75",
            "gnitset"
        ]
        
        output_buffer = ""
        
        # Helper to write input
        def write_input(text):
            print(f"Sending input: {text}")
            process.stdin.write(text + "\n")
            process.stdin.flush()

        # Simple verification loop
        # We will read line by line and if we see "You: ", we send input.
        # IF we match expected output, we mark it passed.
        
        current_input_idx = 0
        passed_checks = 0
        
        start_time = time.time()
        while time.time() - start_time < 45: # 45s timeout
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            print(f"Agent Output: {line}")
            output_buffer += line + "\n"
            
            # Check for prompt
            if "Connected to MCP Server" in line:
                print("Agent connected successfully.")
                # Send first input
                write_input(inputs[0])
                current_input_idx += 1
                
            # Check for answers
            if "75" in line and "Agent:" in line and passed_checks == 0:
                print("Verified sum calculation!")
                passed_checks += 1
                write_input(inputs[1])
                current_input_idx += 1
            
            if "gnitset" in line and "Agent:" in line and passed_checks == 1:
                print("Verified string reversal!")
                passed_checks += 1
                write_input(inputs[2])
                current_input_idx += 1
            
            # Check for UUID (roughly) - looking for dashes and length
            if passed_checks == 2 and "Agent:" in line:
                # UUID format: 8-4-4-4-12
                # We'll just check for basic structure or "calling tool: generate_uuid" roughly
                # But here we want to see the Agent's answer.
                # Assuming the agent prints "Agent: <uuid>"
                import re
                if re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', line):
                    print("Verified UUID generation!")
                    passed_checks += 1
                    write_input(inputs[3])
                    current_input_idx += 1

            if passed_checks == 3 and "Agent:" in line:
                 if "4" in line: # Expecting count of 4
                     print("Verified word count!")
                     passed_checks += 1
                     write_input("quit")
                     break
                
        if passed_checks == 4:
            print("SUCCESS: All tests passed (4/4).")
        else:
            print(f"FAILURE: Only passed {passed_checks}/4 checks.")
    except Exception as e:
        print(f"Test failed with exception: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            
if __name__ == "__main__":
    run_test()
