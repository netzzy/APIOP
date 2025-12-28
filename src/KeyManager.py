"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager 
import TDFunctions as TDF
import json
import os 
import time

class APIKeyManagerExt:
    """
    APIKeyManagerExt manages API keys stored in a JSON file within a TouchDesigner component.
    Each API key is associated with an API server.
    """
    def __init__(self, ownerComp):
        # The component to which this extension is attached
        self.ownerComp = ownerComp
        # Load the API keys from the JSON file
        self.load_keys()

    def HasKey(self, apiServer):
        """
        Check if an API key exists for the specified server.
        Returns True if the key exists and is valid, False otherwise.
        """
        key = self.keys.get(apiServer)
        return bool(key and len(key) > 10)

    def GetServerKey(self, apiServer, fallback_server=None):
        """
        Get the API key for the specified server.
        If the key doesn't exist and fallback_server is provided, try that instead.
        Returns (key, actual_server) tuple.
        """
        # First try the requested server
        key = self.keys.get(apiServer)
        if key and len(str(key)) > 10:
            return key, apiServer
            
        # Try fallback if provided
        if fallback_server:
            key = self.keys.get(fallback_server)
            if key and len(str(key)) > 10:
                return key, fallback_server
                
        # No valid key found
        error_msg = f"No valid API key found for '{apiServer}'"
        if fallback_server:
            error_msg += f" or fallback '{fallback_server}'"
        raise ValueError(error_msg)
    
    def Storekey(self, apiServer, apiKey):
        """
        Store or update an API key associated with a specific API server.
        """
        self.keys[apiServer] = apiKey
        self.save_keys()

    def Retrievekey(self, apiServer):
        """
        Retrieve an API key associated with a specific API server.
        Returns None if the key does not exist.
        """
        return self.keys.get(apiServer)

    def Clearkeys(self):
        """
        Clear all stored API keys.
        """
        self.keys = {}
        # self.save_keys()

    def load_keys(self):
        """
        Load the API keys from the JSON file. If the file doesn't exist and the path is a full path, create it with an empty key list.
        Do not create or save if the path is relative.
        """
        self.keys = {}

        keyfile = self.ownerComp.par.Keyfile.eval()
        
        if os.path.exists(keyfile):
            try:
                with open(keyfile, 'r') as f:
                    self.keys = json.load(f)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                pass

    def save_keys(self):
        """
        Save the API keys to the JSON file.
        """
        keyfile = self.ownerComp.par.Keyfile.eval()

        try:
            with open(keyfile, 'w') as f:
                json.dump(self.keys, f)
        except Exception as e:
            pass