import sys  
import traceback  
import customtkinter as ctk  
from id_creator_premium import IDAppPremium  
try:  
    app = IDAppPremium()  
    print("SUCCESS")  
except Exception as e:  
    traceback.print_exc()  
