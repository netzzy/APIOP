from AopUtil import AopUtil


class AOP(AopUtil):

    def __init__(self, ownerComp):
        # Initialize parent class first
        super().__init__(ownerComp)
        
        self.ownerComp = ownerComp 
        self.logger = op('Logger').ext.Logger if op('Logger') else print # Basic fallback logging
        self.logger.log('AOP initialized', level='INFO')
        
        self.key_manager = self.ownerComp.op('key_manager').ext.APIKeyManagerExt
        
        # Setup custom parameters
        self.setup_parameters()
        
    def setup_parameters(self):
        """Create global parameters for the AOP container."""
        # Create Output directory parameter (folder type)
        self.create_parameter('Outputdir', 'folder', page='Config',
                            label='Output Directory',
                            default='output',
                            help_text='Global output directory for generated content')
        
    def Getkey(self, apiServer, fallback_server=None):
        """
        Get an API key for the specified server using KeyManager.
        
        Args:
            apiServer (str): The API server name to get the key for
            fallback_server (str, optional): Fallback server name if primary key not found
            
        Returns:
            str: The API key for the specified server
            
        Raises:
            ValueError: If no valid key is found for the server(s)
        """
        key, _ = self.key_manager.GetServerKey(apiServer, fallback_server)
        return key
