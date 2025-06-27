
def interpolateColor(value, max_Value=255, Color1=(234,51,247), color2=(234,51,247)):

    # Calculate the interpolation factor
    factor = value / max_Value

    # Interpolate between blue and orange
    r = int(Color1[0] * (1 - factor) + color2[0] * factor)
    g = int(Color1[1] * (1 - factor) + color2[1] * factor)
    b = int(Color1[2] * (1 - factor) + color2[2] * factor)

    return (r, g, b)

def blendColors(color1, color2, blend_factor):
    """
    Blend two colors together based on the blend factor.
    
    Args:
    color1 (tuple): The first color as an (R, G, B) tuple.
    color2 (tuple): The second color as an (R, G, B) tuple.
    blend_factor (float): A value between 0 (color1) and 1 (color2) representing the blend factor.

    Returns:
    tuple: The blended color as an (R, G, B) tuple.
    """
    
    blend_factor = max(0, min(1, blend_factor))
    
    blended_color = (
        int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor),
        int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor),
        int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
    )

    return blended_color

class DynamicColor():
    def __init__(self, OBF = None,BF=0.0,OTC = None, TC=(0,0,0,1), C=(0,0,0,1)):
        self.color = C
        self.targetColor = TC
        self.Dirty = True
        if OTC == None:
            self.orginalTargetColor = TC
        else:
            self.orginalTargetColor = OTC
        if OBF == None:
            self.orginalBlendFactor = BF
        else:
            self.orginalBlendFactor = OBF
        self.blendFactor = BF
        #print(f"color: {self.color} targetColor: {self.targetColor} orginalBlendFactor: {self.orginalBlendFactor} blendFactor: {self.blendFactor}")
    
    def setColor(self, color):
        self.color = color
    def setTargetColor(self, targetColor, ResetBlendFactor = False):
        if ResetBlendFactor: self.blendFactor = 0.0
        self.targetColor = targetColor
    def setOrginalTargetColor(self, orginalTargetColor):
        self.orginalTargetColor = orginalTargetColor
    def setOrginalBlendFactor(self,orginalBlendFactor):
        self.orginalBlendFactor = orginalBlendFactor
    def setBlendFactor(self, blendFactor):
        self.blendFactor = blendFactor
    
    def getColor(self):
        return(self.color)
    def getTargetColor(self):
        return(self.targetColor)
    def getOrginalTargetColor(self):
        return(self.orginalTargetColor)
    def getOrginalBlendFactor(self):
        return(self.orginalBlendFactor)
    def getBlendFactor(self):
        return(self.blendFactor)
    def getInfo(self,p=""):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{p}color:                {self.color} \n{p}orginalTargetColor:   {self.orginalTargetColor} \n{p}targetColor:          {self.targetColor} \n{p}orginalBlendFactor:   {self.orginalBlendFactor} \n{p}blendFactor:          {self.blendFactor}")
    
    def isDirty(self)->bool:
        return self.Dirty
    
    def Update(self,updateRate = (1/5),deltaTime=1.0):
        self.blendFactor = min(self.blendFactor + updateRate * deltaTime,1.0)
        self.blendColor(self.blendFactor)
        if self.color == self.targetColor:
            self.Dirty = False
        else:
            self.Dirty = True
        
    def Reset(self):
        self.blendFactor = self.getOrginalBlendFactor()
        self.color = (0,0,0)
        
        
        
        
        
    def blendColor(self, blend_factor):
        """
        Blend two colors together based on the blend factor.

        Args:
        color1 (tuple): The first color as an (R, G, B) tuple.
        color2 (tuple): The second color as an (R, G, B) tuple.
        blend_factor (float): A value between 0 (color1) and 1 (color2) representing the blend factor.

        Returns:
        tuple: The blended color as an (R, G, B) tuple.
        """

        blend_factor = max(0, min(1, blend_factor))

        blended_color = (
            int(self.color[0] * (1 - blend_factor) + self.targetColor[0] * blend_factor),
            int(self.color[1] * (1 - blend_factor) + self.targetColor[1] * blend_factor),
            int(self.color[2] * (1 - blend_factor) + self.targetColor[2] * blend_factor)
        )
        self.color = blended_color
    
    
    
    
    
    
    
    