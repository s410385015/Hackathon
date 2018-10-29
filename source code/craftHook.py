import PyHook3
import pythoncom
import threading
import sys
import pyautogui

class CraftHook:
    def __init__(self):
        t = threading.Thread(target = self.SetUp)  
        self.flag=True
        pyautogui.PAUSE = 0
        t.start()

    def handleCraftEvent(self,event):
        print(event['message_type'])

    def OnMouseEvent(self,event):
        '''
        print('MessageName:',event.MessageName)
        print('Message:',event.Message)
        print('Time:',event.Time)
        print('Window:',event.Window)
        print('WindowName:',event.WindowName)
        print('Position:',event.Position)
        print('Wheel:',event.Wheel)
        print('Injected:',event.Injected)
        print('---')
        '''
        return True
    def OnKeyboardEvent(self,event):
        '''
        print('MessageName:',event.MessageName)
        print('Message:',event.Message)
        print('Time:',event.Time)
        print('Window:',event.Window)
        print('WindowName:',event.WindowName)
        print('Ascii:', event.Ascii, chr(event.Ascii))
        print('Key:', event.Key)
        print('KeyID:', event.KeyID)
        print('ScanCode:', event.ScanCode)
        print('Extended:', event.Extended)
        print('Injected:', event.Injected)
        print('Alt', event.Alt)
        print('Transition', event.Transition)
        print('---')
        '''
        if event.KeyID == 56 and event.ScanCode==9:
            self.Roll(-10)
            return False
        if event.KeyID == 57 and event.ScanCode==10:
            self.Roll(10)
            return False
        if event.KeyID == 173:
            self.Press("m")
            return False
        return True

    def SetUp(self):
        hm = PyHook3.HookManager()
        #hm.MouseAllButtonsDown = self.OnMouseEvent
        hm.KeyDown = self.OnKeyboardEvent
        #hm.HookMouse()
        hm.HookKeyboard()
        while self.flag:
            pythoncom.PumpWaitingMessages()
   
    def close(self):
        self.flag=False


    def Press(self,cmd):
        pyautogui.press(cmd)
    
    def Roll(self,value):
        pyautogui.scroll(value)