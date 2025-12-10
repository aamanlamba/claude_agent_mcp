
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
            "Create a 1-slide presentation about testing",
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
        while time.time() - start_time < 60: # 60s timeout (PPTX might take longer)
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
            
            # Check for UUID (roughly) 
            if passed_checks == 2 and "Agent:" in line:
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
                     write_input(inputs[4])
                     current_input_idx += 1
            
            # Check for PPTX creation
            # The output likely contains "I have created the presentation..." or similar.
            # We also might see "[Agent] Calling tool: code_execution" if it uses code execution to utilize the skill?
            # Or it might just return the result.
            # Skills work by loading code and executing it.
            # Let's check for "presentation" or "slide" in the response.
            if passed_checks == 4 and "Agent:" in line:
                if "presentation" in line.lower() or "slide" in line.lower():
                    print("Verified PPTX creation response!")
                    passed_checks += 1
                    write_input("quit")
                    break
                
        if passed_checks == 5:
            print("SUCCESS: All tests passed (5/5).")
        else:
            print(f"FAILURE: Only passed {passed_checks}/5 checks.")
    except Exception as e:
        print(f"Test failed with exception: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            
if __name__ == "__main__":
    run_test()
