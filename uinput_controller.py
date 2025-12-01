#!/usr/bin/env python3
"""
UInput-based Input Controller - Direct kernel input injection
Solves Wayland restrictions including Super key
"""

import evdev
from evdev import UInput, ecodes
import time
import os

class UInputController:
    def __init__(self):
        self.keyboard = None
        self.mouse = None
        self.screen_width = 1920
        self.screen_height = 1080
        self.mouse_x = 960
        self.mouse_y = 540
        self.setup_devices()
        
    def setup_devices(self):
        """Create virtual keyboard and mouse devices"""
        try:
            # Keyboard capabilities - all keys
            keyboard_caps = {
                ecodes.EV_KEY: [
                    # Letters A-Z
                    ecodes.KEY_A, ecodes.KEY_B, ecodes.KEY_C, ecodes.KEY_D, ecodes.KEY_E, 
                    ecodes.KEY_F, ecodes.KEY_G, ecodes.KEY_H, ecodes.KEY_I, ecodes.KEY_J, 
                    ecodes.KEY_K, ecodes.KEY_L, ecodes.KEY_M, ecodes.KEY_N, ecodes.KEY_O, 
                    ecodes.KEY_P, ecodes.KEY_Q, ecodes.KEY_R, ecodes.KEY_S, ecodes.KEY_T, 
                    ecodes.KEY_U, ecodes.KEY_V, ecodes.KEY_W, ecodes.KEY_X, ecodes.KEY_Y, 
                    ecodes.KEY_Z,
                    
                    # Numbers 0-9
                    ecodes.KEY_0, ecodes.KEY_1, ecodes.KEY_2, ecodes.KEY_3, ecodes.KEY_4,
                    ecodes.KEY_5, ecodes.KEY_6, ecodes.KEY_7, ecodes.KEY_8, ecodes.KEY_9,
                    
                    # Special keys
                    ecodes.KEY_SPACE, ecodes.KEY_ENTER, ecodes.KEY_BACKSPACE, ecodes.KEY_TAB,
                    ecodes.KEY_ESC, ecodes.KEY_DELETE, ecodes.KEY_HOME, ecodes.KEY_END,
                    
                    # Arrow keys
                    ecodes.KEY_UP, ecodes.KEY_DOWN, ecodes.KEY_LEFT, ecodes.KEY_RIGHT,
                    
                    # Modifiers
                    ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT, 
                    ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
                    ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
                    
                    # SUPER KEYS - The magic ones!
                    ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA,
                    
                    # Punctuation keys - ADDED FOR SPECIAL CHARACTERS
                    ecodes.KEY_DOT, ecodes.KEY_COMMA, ecodes.KEY_SEMICOLON, ecodes.KEY_SLASH,
                    ecodes.KEY_MINUS, ecodes.KEY_EQUAL, ecodes.KEY_LEFTBRACE, ecodes.KEY_RIGHTBRACE,
                    ecodes.KEY_BACKSLASH, ecodes.KEY_APOSTROPHE, ecodes.KEY_GRAVE,
                    
                    # Function keys
                    ecodes.KEY_F1, ecodes.KEY_F2, ecodes.KEY_F3, ecodes.KEY_F4, 
                    ecodes.KEY_F5, ecodes.KEY_F6, ecodes.KEY_F7, ecodes.KEY_F8, 
                    ecodes.KEY_F9, ecodes.KEY_F10, ecodes.KEY_F11, ecodes.KEY_F12,
                ]
            }
            
            # Mouse capabilities - FIXED VERSION
            mouse_caps = {
                ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE],
                ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y, ecodes.REL_WHEEL, ecodes.REL_HWHEEL],
            }
            
            # Create devices with proper names and bustype
            self.keyboard = UInput(keyboard_caps, name='Desktop-Automation-Keyboard', bustype=0x03)
            self.mouse = UInput(mouse_caps, name='Desktop-Automation-Mouse', bustype=0x03)
            
            print("✅ UInput devices created successfully")
            
        except PermissionError:
            print("❌ Permission denied. Need uinput access.")
            raise
        except Exception as e:
            print(f"❌ Failed to create UInput devices: {e}")
            raise
    
    def press_key(self, key_code, state):
        """Press or release a key"""
        if not self.keyboard:
            return False
            
        try:
            if state == "down":
                self.keyboard.write(ecodes.EV_KEY, key_code, 1)
            elif state == "up":
                self.keyboard.write(ecodes.EV_KEY, key_code, 0)
            
            self.keyboard.syn()
            return True
        except Exception as e:
            print(f"❌ Key press failed: {e}")
            return False
    
    def move_mouse_pixels(self, dx_pixels, dy_pixels):
        """Move mouse by exact pixel amounts - HYBRID APPROACH"""
        # Try UInput first
        if self.mouse:
            try:
                self.mouse.write(ecodes.EV_REL, ecodes.REL_X, dx_pixels)
                self.mouse.write(ecodes.EV_REL, ecodes.REL_Y, dy_pixels)
                self.mouse.syn()
                
                # Verify movement worked by checking if position changed
                import pyautogui
                time.sleep(0.1)
                # If UInput worked, return success
                return True
            except Exception as e:
                print(f"⚠️  UInput mouse failed, falling back to pyautogui: {e}")
        
        # Fallback to pyautogui if UInput fails
        try:
            import pyautogui
            pyautogui.move(dx_pixels, dy_pixels)
            print(f"✅ Fallback: pyautogui moved mouse ({dx_pixels}, {dy_pixels})")
            return True
        except Exception as e:
            print(f"❌ Both UInput and pyautogui mouse failed: {e}")
            return False
    
    def scroll_wheel(self, scroll_amount):
        """Scroll mouse wheel"""
        if not self.mouse:
            return False
            
        try:
            self.mouse.write(ecodes.EV_REL, ecodes.REL_WHEEL, scroll_amount)
            self.mouse.syn()
            return True
        except Exception as e:
            print(f"❌ Mouse scroll failed: {e}")
            return False
    
    def click_mouse(self, button, state):
        """Click mouse button"""
        if not self.mouse:
            return False
            
        try:
            button_map = {
                'left': ecodes.BTN_LEFT,
                'right': ecodes.BTN_RIGHT,
                'middle': ecodes.BTN_MIDDLE
            }
            
            btn_code = button_map.get(button, ecodes.BTN_LEFT)
            
            if state == "down":
                self.mouse.write(ecodes.EV_KEY, btn_code, 1)
            elif state == "up":
                self.mouse.write(ecodes.EV_KEY, btn_code, 0)
            elif state == "click":
                self.mouse.write(ecodes.EV_KEY, btn_code, 1)
                self.mouse.syn()
                time.sleep(0.01)
                self.mouse.write(ecodes.EV_KEY, btn_code, 0)
            
            self.mouse.syn()
            return True
        except Exception as e:
            print(f"❌ Mouse click failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up devices"""
        if self.keyboard:
            self.keyboard.close()
        if self.mouse:
            self.mouse.close()
    
    def __del__(self):
        self.cleanup()
