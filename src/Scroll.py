from AopUtil import AopUtil


class Scroll(AopUtil):

    def __init__(self, ownerComp):
        # Initialize parent class first
        super().__init__(ownerComp)
        
        self.ownerComp = ownerComp 
        
        # Setup custom parameters
        self.setup_parameters()
    
    def setup_parameters(self):
        """Create custom parameters for scrolling functionality."""
        # Create Max parameter
        self.create_parameter('Max', 'int', page='Custom',
                            label='Max',
                            default=5,
                            norm_min=1,
                            help_text='Maximum value for cursor (range: 0 to Max)')
        
        # Create Cursor parameter (current position)
        self.create_parameter('Cursor', 'int', page='Custom',
                            label='Cursor',
                            default=0,
                            norm_min=0,
                            help_text='Current cursor position (0 to Max)')
        
        # Create Next pulse button
        self.create_parameter('Next', 'pulse', page='Custom',
                            label='Next',
                            help_text='Move cursor forward (wraps to 0 when exceeding Max)')
        
        # Create Prev pulse button
        self.create_parameter('Prev', 'pulse', page='Custom',
                            label='Prev',
                            help_text='Move cursor backward (wraps to Max when below 0)')
    
    def Next(self):
        """Pulse callback for Next button - increments cursor with wrap-around."""
        current = self.ownerComp.par.Cursor.eval()
        max_val = self.ownerComp.par.Max.eval()
        
        # Increment cursor
        new_value = current + 1
        
        # Wrap around to 0 if exceeding max
        if new_value > max_val:
            new_value = 0
        
        self.ownerComp.par.Cursor = new_value
    
    def Prev(self):
        """Pulse callback for Prev button - decrements cursor with wrap-around."""
        current = self.ownerComp.par.Cursor.eval()
        max_val = self.ownerComp.par.Max.eval()
        
        # Decrement cursor
        new_value = current - 1
        
        # Wrap around to max if below 0
        if new_value < 0:
            new_value = max_val
        
        self.ownerComp.par.Cursor = new_value
