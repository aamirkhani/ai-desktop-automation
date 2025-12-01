#!/usr/bin/env python3
"""
AI Desktop Automation with LLM - Production Version
"""

import argparse
import base64
import json
import os
import time
import subprocess
from datetime import datetime
from openai import OpenAI
from uinput_controller import UInputController
from evdev import ecodes

class DesktopAutomator:
    def __init__(self, verbose=True):
        self.verbose = verbose
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key)
        self.action_history = []
        self.screenshot_count = 0
        
        # Initialize UInput controller
        self.input_controller = UInputController()
        
        # Configure pyautogui for mouse fallback
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.05
        
        # Ensure generated directory exists
        os.makedirs('generated', exist_ok=True)
        
    def take_screenshot(self):
        """Take screenshot using pyautogui"""
        import pyautogui
        self.screenshot_count += 1
        filename = f'generated/screenshot_{self.screenshot_count:04d}.png'
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        if self.verbose:
            print(f'[VERBOSE] Screenshot saved: {filename}')
        return filename
    
    def validate_and_clean_action(self, action):
        """Validate and clean action"""
        if not isinstance(action, dict):
            return {"action": "DO_NOTHING", "justification": "Invalid action format"}
        
        cleaned_action = {}
        
        if "action" in action:
            cleaned_action["action"] = action["action"]
        else:
            return {"action": "DO_NOTHING", "justification": "Missing action field"}
        
        # Optional fields
        if "state" in action:
            cleaned_action["state"] = action["state"]
        if "value" in action:
            cleaned_action["value"] = action["value"]
        
        # Justification field
        if "justification" in action:
            cleaned_action["justification"] = action["justification"]
        else:
            cleaned_action["justification"] = "No justification provided"
        
        return cleaned_action
    
    def execute_action(self, action):
        """Execute action using UInput"""
        action = self.validate_and_clean_action(action)
        
        if self.verbose:
            print(f'[EXECUTE] Action: {action}')
        
        try:
            action_type = action.get('action')
            
            if action_type == 'DO_NOTHING':
                return True
            
            # Mouse movement
            elif action_type in ['REL_X', 'REL_Y']:
                value = action.get('value', 0)
                import pyautogui
                if action_type == 'REL_X':
                    pyautogui.move(value, 0)
                else:
                    pyautogui.move(0, value)
                return True
                
            # Mouse buttons
            elif action_type in ['BTN_LEFT', 'BTN_RIGHT', 'BTN_MIDDLE']:
                button_map = {
                    'BTN_LEFT': 'left',
                    'BTN_RIGHT': 'right', 
                    'BTN_MIDDLE': 'middle'
                }
                button = button_map[action_type]
                state = action.get('state', 'click')
                return self.input_controller.click_mouse(button, state)
                
            # Keyboard keys
            elif hasattr(ecodes, action_type):
                key_code = getattr(ecodes, action_type)
                state = action.get('state', 'down')
                return self.input_controller.press_key(key_code, state)
                
            # Mouse wheel
            elif action_type == 'REL_WHEEL':
                value = action.get('value', 0)
                return self.input_controller.scroll_wheel(value)
                
            return True
                
        except Exception as e:
            if self.verbose:
                print(f'[ERROR] Failed to execute action: {e}')
            return False
    
    def get_llm_action(self, user_prompt, screenshot_path):
        """Get action from LLM"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(screenshot_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        
        try:
            system_prompt = f"""
You are an AI Agent automating desktop tasks. Perform this task: {user_prompt}

Based on the screenshot, generate the next action using Linux evdev codes in JSON format.

Action history: {json.dumps(self.action_history[-5:], indent=2)}

Use this JSON schema:
{{
  "action": "KEY_A" | "BTN_LEFT" | "REL_X" | "REL_Y" | "REL_WHEEL" | "DO_NOTHING",
  "state": "down" | "up" | "click",
  "value": number (for REL_X, REL_Y, REL_WHEEL only),
  "justification": "Brief explanation"
}}

Supported keys: KEY_A-Z, KEY_0-9, KEY_ENTER, KEY_SPACE, KEY_BACKSPACE, KEY_TAB, 
KEY_ESC, KEY_DELETE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_LEFTSHIFT, 
KEY_LEFTCTRL, KEY_LEFTALT, KEY_LEFTMETA, KEY_DOT, KEY_COMMA, KEY_SEMICOLON, 
KEY_SLASH, KEY_MINUS, KEY_EQUAL, KEY_LEFTBRACE, KEY_RIGHTBRACE, KEY_BACKSLASH, 
KEY_APOSTROPHE, KEY_GRAVE, KEY_F1-F12
"""

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}]}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            
            # Save LLM interaction
            with open(f"generated/LLM_input_{timestamp}.txt", "w") as f:
                f.write(system_prompt)
            with open(f"generated/LLM_output_{timestamp}.txt", "w") as f:
                f.write(content)
            
            # Clean markdown
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0].strip()
            
            return json.loads(content)
            
        except Exception as e:
            if self.verbose:
                print(f'[ERROR] LLM request failed: {e}')
            return {"action": "DO_NOTHING", "justification": "LLM error"}
    
    def run(self, user_prompt, max_iterations=50):
        """Main automation loop"""
        print(f'🚀 Starting automation: {user_prompt}')
        
        for iteration in range(max_iterations):
            if self.verbose:
                print(f'[VERBOSE] === Iteration {iteration + 1} ===')
            
            # Take screenshot
            screenshot_path = self.take_screenshot()
            
            # Get LLM action
            action_response = self.get_llm_action(user_prompt, screenshot_path)
            
            # Handle both single actions and action lists
            if isinstance(action_response, list):
                actions_to_execute = action_response
            else:
                actions_to_execute = [action_response]
            
            # Execute all actions
            for action in actions_to_execute:
                clean_action = self.validate_and_clean_action(action)
                
                # Add to history
                action_with_timestamp = {
                    'timestamp': datetime.now().isoformat(),
                    'action': clean_action
                }
                self.action_history.append(action_with_timestamp)
                
                # Execute action
                success = self.execute_action(clean_action)
                if not success and self.verbose:
                    print(f'[WARNING] Action failed: {clean_action.get("action", "unknown")}')
                
                time.sleep(0.1)
            
            # Keep only last 512 actions
            if len(self.action_history) > 512:
                self.action_history = self.action_history[-512:]
            
            # Check completion
            last_action = actions_to_execute[-1] if actions_to_execute else {}
            if last_action.get('action') == 'DO_NOTHING':
                print('🎉 Task completed')
                break
                
            time.sleep(2)
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'input_controller'):
            self.input_controller.cleanup()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Desktop Automation')
    parser.add_argument('--task', default='open calculator and calculate 5 + 3', 
                       help='Task to perform')
    parser.add_argument('--verbose', action='store_true', default=True,
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    automator = DesktopAutomator(verbose=args.verbose)
    try:
        automator.run(args.task)
    finally:
        automator.cleanup()

if __name__ == '__main__':
    main()
